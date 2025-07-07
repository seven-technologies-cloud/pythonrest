import yaml
import json
import os
import glob # For finding files
import logging
import collections.abc # For deep_merge_dicts type check
from flask import current_app # To get app root path for finding swagger files

from src.e_Infra.g_McpInfra import LlmServiceBase
from src.e_Infra.CustomVariables import SWAGGER_FILES_DIR # Using the conventional directory

logger = logging.getLogger(__name__)

def deep_merge_dicts(source, destination):
    """
    Recursively merges source dict into destination dict.
    - If a key exists in both and both values are dicts, recursively merge.
    - If a key exists in both and both values are lists, concatenate them (optionally de-duplicate simple lists).
    - Otherwise, value from source overwrites value from destination.
    """
    for key, value in source.items():
        if isinstance(value, collections.abc.Mapping): # Check if it's a dict-like object
            destination[key] = deep_merge_dicts(value, destination.get(key, {}))
        elif isinstance(value, list) and isinstance(destination.get(key), list):
            # Simple concatenation for lists like 'tags' or 'servers'.
            # For more complex list merging (e.g., de-duplicating objects by a key),
            # more specific logic would be needed per OpenAPI section.
            destination[key].extend(value)
            # Basic de-duplication for lists of simple hashable items (like strings in a tag list)
            try:
                if all(isinstance(item, collections.abc.Hashable) for item in destination[key]):
                    destination[key] = list(dict.fromkeys(destination[key]))
            except TypeError:
                pass # Cannot de-duplicate if items are not hashable (e.g. list of dicts without a clear key)

        else:
            destination[key] = value
    return destination

class ApiQueryService:
    """
    Service to answer questions about an API using its OpenAPI specification
    (aggregated from multiple files) and a configured LLM.
    """
    def __init__(self, llm_service: LlmServiceBase):
        """
        Initializes the ApiQueryService.
        The OpenAPI spec is loaded upon initialization.

        Args:
            llm_service (LlmServiceBase): An instance of a class that implements LlmServiceBase.
        """
        if not isinstance(llm_service, LlmServiceBase):
            logger.error("Invalid LLM service instance provided. Must implement LlmServiceBase.")
            raise TypeError("llm_service must be an instance of a class implementing LlmServiceBase.")

        self.llm_service = llm_service
        self.api_spec = None
        self._load_and_parse_openapi_specs() # Load and merge specs during initialization

    def _load_and_parse_openapi_specs(self):
        """
        Loads, parses, and merges all OpenAPI specification files found in the
        conventional directory (SWAGGER_FILES_DIR).
        """
        # It's generally better to make paths absolute from the app root if running within Flask
        # or ensure the relative path is correct from where the app is executed.
        # Using current_app.root_path if available (i.e., when running in Flask context).
        # If current_app is not available (e.g. unit tests outside app context),
        # try to use a path relative to this file or assume project root.
        try:
            base_path = current_app.root_path
        except RuntimeError: # Outside of application context
            # Fallback for non-Flask context (e.g. some test runners, direct script exec)
            # This assumes 'src' is a direct child of the project root.
            base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
            logger.warning(f"Flask current_app not available. Using inferred base_path: {base_path} for Swagger files. Ensure this is correct.")

        swagger_dir_path = os.path.join(base_path, SWAGGER_FILES_DIR)

        logger.info(f"Scanning for Swagger YAML files in: {swagger_dir_path}")

        yaml_files = []
        yaml_files.extend(glob.glob(os.path.join(swagger_dir_path, "*.yaml")))
        yaml_files.extend(glob.glob(os.path.join(swagger_dir_path, "*.yml")))

        if not yaml_files:
            logger.error(f"No Swagger YAML files found in {swagger_dir_path}. Cannot build API specification.")
            self.api_spec = { # Provide a minimal valid spec to prevent downstream errors
                "openapi": "3.0.0",
                "info": {"title": "Error: No API Specification Found", "version": "0.0.0",
                         "description": f"No Swagger/OpenAPI YAML files were found in the expected directory: {swagger_dir_path}"},
                "paths": {},
                "components": {}
            }
            return

        # Initialize base aggregated spec
        aggregated_spec = {
            "openapi": "3.0.0", # Assuming OpenAPI 3.0.0
            "info": None, # To be populated
            "paths": {},
            "components": {"schemas": {}, "responses": {}, "parameters": {}, "examples": {},
                           "requestBodies": {}, "headers": {}, "securitySchemes": {}, "links": {}, "callbacks": {}},
            "tags": [],
            "servers": [],
            "security": [], # Default to no security unless specified
            "externalDocs": None
        }

        # Sort files for consistent merging order (helps with "last one wins" for `info`)
        yaml_files.sort()

        # Try to find a primary info file
        primary_info_files = ["_info.yaml", "main.yaml", "openapi.yaml", "_openapi_info.yaml"] # Order of preference
        info_obj_found = False

        # Process primary info files first if they exist
        processed_info_files = set()
        for info_file_name in primary_info_files:
            full_info_path = os.path.join(swagger_dir_path, info_file_name)
            if full_info_path in yaml_files:
                try:
                    with open(full_info_path, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f)
                        if content and isinstance(content.get("info"), dict):
                            aggregated_spec["info"] = content["info"]
                            logger.info(f"Loaded primary 'info' object from: {info_file_name}")
                            info_obj_found = True
                            # Merge other top-level keys from this primary file too
                            for key, value in content.items():
                                if key not in ["openapi", "info", "paths", "components"]: # These are handled specially
                                    if key in ["tags", "servers"] and isinstance(value, list):
                                        aggregated_spec.setdefault(key, []).extend(value)
                                    else: # Last one wins for other top-level keys
                                        aggregated_spec[key] = value
                            processed_info_files.add(full_info_path)
                            break # Found primary info, stop looking
                except Exception as e:
                    logger.error(f"Error loading or parsing primary info file {full_info_path}: {e}", exc_info=True)


        # Merge all files
        for yaml_file in yaml_files:
            if yaml_file in processed_info_files and info_obj_found: # If already processed for info and other top-level keys
                 # Only merge paths and components from this file, info already taken
                try:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f)
                        if not content: continue
                        if isinstance(content.get("paths"), dict):
                            deep_merge_dicts(content["paths"], aggregated_spec["paths"])
                        if isinstance(content.get("components"), dict):
                            deep_merge_dicts(content["components"], aggregated_spec["components"])
                        # If this primary info file also had tags/servers, they were already added.
                        # We could add a more complex de-duplication for tags/servers here if needed.
                except Exception as e:
                    logger.error(f"Error loading or parsing {yaml_file} (after info processing): {e}", exc_info=True)
                continue # Move to next file

            # Standard processing for other files or if no primary info file was fully processed
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    if not content: # Skip empty files
                        logger.warning(f"Swagger file {yaml_file} is empty or invalid. Skipping.")
                        continue

                    # Handle 'info' if not yet found from a primary file
                    if not info_obj_found and isinstance(content.get("info"), dict):
                        aggregated_spec["info"] = content["info"] # First one alphabetically wins if no primary
                        info_obj_found = True
                        logger.info(f"Loaded 'info' object from: {os.path.basename(yaml_file)}")

                    # Merge paths
                    if isinstance(content.get("paths"), dict):
                        deep_merge_dicts(content["paths"], aggregated_spec["paths"])

                    # Merge components
                    if isinstance(content.get("components"), dict):
                        deep_merge_dicts(content["components"], aggregated_spec["components"])

                    # Merge other top-level keys (tags, servers, security, externalDocs)
                    for key in ["tags", "servers", "security", "externalDocs"]:
                        if key in content:
                            if key in ["tags", "servers"] and isinstance(content[key], list): # List types
                                aggregated_spec.setdefault(key, []).extend(content[key])
                            elif key == "externalDocs" and isinstance(content[key], dict): # Object type
                                aggregated_spec[key] = content[key] # Last one wins
                            elif key == "security" and isinstance(content[key], list): # List of security requirement objects
                                aggregated_spec.setdefault(key, []).extend(content[key]) # Simple extend for now
                            # else:
                                # Could add more specific merges for other top-level keys if needed

                    logger.info(f"Merged content from: {os.path.basename(yaml_file)}")

            except yaml.YAMLError as e:
                logger.error(f"Error parsing YAML from {yaml_file}: {e}", exc_info=True)
            except Exception as e:
                logger.error(f"An unexpected error occurred while processing {yaml_file}: {e}", exc_info=True)

        # Post-process lists like tags and servers for basic de-duplication
        if aggregated_spec.get("tags"):
            # De-duplicate tags by 'name'
            unique_tags = []
            seen_tag_names = set()
            for tag in aggregated_spec["tags"]:
                if isinstance(tag, dict) and tag.get("name") and tag["name"] not in seen_tag_names:
                    unique_tags.append(tag)
                    seen_tag_names.add(tag["name"])
            aggregated_spec["tags"] = unique_tags

        if aggregated_spec.get("servers"):
            # De-duplicate servers by 'url'
            unique_servers = []
            seen_server_urls = set()
            for server in aggregated_spec["servers"]:
                if isinstance(server, dict) and server.get("url") and server["url"] not in seen_server_urls:
                    unique_servers.append(server)
                    seen_server_urls.add(server["url"])
            aggregated_spec["servers"] = unique_servers

        # If no info object was found at all, provide a default
        if not aggregated_spec["info"]:
            aggregated_spec["info"] = {
                "title": "Aggregated API Specification",
                "version": "1.0.0",
                "description": "Automatically aggregated from multiple Swagger/OpenAPI files."
            }
            logger.info("No 'info' object found in any Swagger file; using generic default.")

        self.api_spec = aggregated_spec
        logger.info("All Swagger files processed and merged.")


    def answer_api_question(self, question: str) -> str:
        """
        Answers a question about the API using the loaded OpenAPI spec and LLM.
        """
        if self.api_spec is None or not self.api_spec.get("paths"): # Check if spec is meaningfully loaded
            logger.error("API spec is not loaded or is empty. Cannot answer question.")
            # Attempt to reload, though __init__ should have done this.
            try:
                self._load_and_parse_openapi_specs()
                if self.api_spec is None or not self.api_spec.get("paths"):
                     # Check if it's the "No API Specification Found" error spec
                    if self.api_spec and self.api_spec.get("info", {}).get("title") == "Error: No API Specification Found":
                        return f"Cannot answer question: {self.api_spec['info']['description']}"
                    raise RuntimeError("API specification is not loaded or is empty. Cannot answer questions.")
            except Exception as e:
                 return f"Cannot answer question: API specification could not be loaded due to error: {e}"


        if not question:
            logger.warning("Answer_api_question called with an empty question.")
            return "Please provide a question about the API."

        try:
            spec_str = json.dumps(self.api_spec, indent=2)
            # Truncation logic might need to be more aggressive if specs are huge
            # Or consider sending only relevant parts based on question analysis (more complex)
            if len(spec_str) > 30000: # Increased limit slightly, but still a concern for very large specs
                spec_str = spec_str[:30000] + "\n... (specification truncated due to size)"
                logger.warning("Aggregated API spec string was truncated for the LLM prompt due to size.")
        except Exception as e:
            logger.error(f"Could not serialize aggregated API spec to string for prompt: {e}", exc_info=True)
            spec_str = "Error: Could not serialize API specification for the prompt."

        prompt = f"""You are an expert AI assistant knowledgeable about a specific API.
Your task is to answer questions about this API based on its OpenAPI specification.

Here is the OpenAPI specification (or a relevant part of it):
--- START OF API SPECIFICATION ---
{spec_str}
--- END OF API SPECIFICATION ---

User's question: "{question}"

Based on the provided API specification and the user's question, please provide a clear, concise, and accurate answer.
If the information is not available in the specification, state that clearly.
Do not make up information not present in the spec.
"""

        try:
            answer = self.llm_service.generate_text(prompt)
            logger.info(f"Successfully generated answer for question: '{question}' using {type(self.llm_service).__name__}")
            return answer
        except RuntimeError as e:
            logger.error(f"Failed to get answer from LLM service ({type(self.llm_service).__name__}) for question '{question}': {e}", exc_info=True)
            raise RuntimeError(f"Could not get an answer from the AI service ({type(self.llm_service).__name__}): {e}")
        except Exception as e:
            logger.error(f"Unexpected error in answer_api_question for question '{question}': {e}", exc_info=True)
            raise RuntimeError(f"An unexpected error occurred while trying to answer the question: {e}")
