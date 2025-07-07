import yaml
import json
import os
import glob
import logging
import collections.abc
from flask import current_app

from src.e_Infra.g_McpInfra import LlmServiceBase

logger = logging.getLogger(__name__)

# Corrected fixed conventional path relative to the generated project root
# This means ApiQueryService expects a 'config' folder at the same level as 'src'
PROJECT_ROOT_CONFIG_SWAGGER_DIR = "config/"

def deep_merge_dicts(source, destination):
    """
    Recursively merges source dict into destination dict.
    - If a key exists in both and both values are dicts, recursively merge.
    - If a key exists in both and both values are lists, concatenate them (optionally de-duplicate simple lists).
    - Otherwise, value from source overwrites value from destination.
    """
    for key, value in source.items():
        if isinstance(value, collections.abc.Mapping):
            destination[key] = deep_merge_dicts(value, destination.get(key, {}))
        elif isinstance(value, list) and isinstance(destination.get(key), list):
            destination[key].extend(value)
            try:
                if all(isinstance(item, collections.abc.Hashable) for item in destination[key]):
                    destination[key] = list(dict.fromkeys(destination[key]))
            except TypeError:
                pass
        else:
            destination[key] = value
    return destination

class ApiQueryService:
    def __init__(self, llm_service: LlmServiceBase):
        if not isinstance(llm_service, LlmServiceBase):
            logger.error("Invalid LLM service instance provided. Must implement LlmServiceBase.")
            raise TypeError("llm_service must be an instance of a class implementing LlmServiceBase.")
        self.llm_service = llm_service
        self.api_spec = None
        self._load_and_parse_openapi_specs()

    def _determine_project_root(self) -> str:
        """Determines the project root path."""
        try:
            # If current_app.root_path is .../Project/src, project_root is .../Project
            # If current_app.root_path is .../Project (e.g. app.py at root), it's already project_root
            # This needs to be robust. A common pattern is that app.py (and thus current_app.root_path)
            # is at the true project root, or one level inside an 'instance' folder.
            # If 'src' is a package and the app is run from outside 'src', current_app.root_path might be the project root.
            # If the app is run from within 'src', current_app.root_path might be 'src'.

            # Assuming app.py is at the root of the generated project, alongside 'src' and 'config'
            # Then current_app.root_path would be the project root.
            # If app.py is inside 'src', then current_app.root_path is '.../src', so we go up one level.

            # A common way for Flask apps: current_app.root_path is the app's root folder.
            # If your app's main file (e.g. app.py) is at GeneratedProjectRoot/Project/app.py, then current_app.root_path is '.../Project/'.
            # The 'config' directory is expected to be a direct child of this path.
            project_root = current_app.root_path
            logger.info(f"Attempting to use current_app.root_path: {project_root}")
            # Verification: Check if 'config' and 'src' are plausible from this root_path
            # This is a sanity check, actual file/dir existence is checked later.
            if os.path.isdir(os.path.join(project_root, "src")) or os.path.isdir(os.path.join(project_root, PROJECT_ROOT_CONFIG_SWAGGER_DIR)):
                logger.info(f"Using current_app.root_path as project_root: {project_root}")
                return project_root
            else:
                # This case might occur if current_app.root_path is, for example, an 'instance' folder
                # or deep inside 'src'. We try to go up one level.
                project_root_adjusted = os.path.abspath(os.path.join(project_root, ".."))
                logger.warning(f"current_app.root_path ({project_root}) does not seem to be the project root. Trying its parent: {project_root_adjusted}")
                # Add a more specific check if this adjusted path is likely the project root
                if os.path.isdir(os.path.join(project_root_adjusted, "src")) and os.path.isdir(os.path.join(project_root_adjusted, PROJECT_ROOT_CONFIG_SWAGGER_DIR)):
                    logger.info(f"Using adjusted project_root (parent of current_app.root_path): {project_root_adjusted}")
                    return project_root_adjusted
                # If still not found, we'll fall through to the general fallback, which is risky.
                logger.error(f"Could not confidently determine project root from current_app.root_path: {project_root}. Proceeding to fallback, but this may be unreliable.")
                # Fall through to the broader fallback if adjustment doesn't work.

        except RuntimeError: # Outside of application context
            logger.warning("Flask current_app not available. Using fallback path determination.")
            pass # Fall through to the next determination method

        # Fallback path determination if Flask context is not available or didn't yield a good root
        # Assumes ApiQueryService.py is at YourProjectRoot/src/b_Application/b_Service/c_McpService/ApiQueryService.py
        # We want to go up 4 levels to YourProjectRoot/ (which is .../Project/ in the template structure)
        current_file_dir = os.path.abspath(os.path.dirname(__file__))
        project_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", "..", ".."))
        logger.info(f"Determined project_root via fallback: {project_root}")
        return project_root


    def _load_and_parse_openapi_specs(self):
        project_root = self._determine_project_root()
        swagger_base_dir_path = os.path.join(project_root, PROJECT_ROOT_CONFIG_SWAGGER_DIR)

        logger.info(f"Scanning for Swagger YAML files recursively in: {swagger_base_dir_path}")

        yaml_files = []
        if not os.path.isdir(swagger_base_dir_path):
            logger.error(f"Swagger directory does not exist: {swagger_base_dir_path}")
        else:
            for root, _, files in os.walk(swagger_base_dir_path):
                for file in files:
                    if file.endswith((".yaml", ".yml")):
                        yaml_files.append(os.path.join(root, file))

        if not yaml_files:
            logger.error(f"No Swagger YAML files found in {swagger_base_dir_path} or its subdirectories. Cannot build API specification.")
            self.api_spec = {
                "openapi": "3.0.0",
                "info": {"title": "Error: No API Specification Found", "version": "0.0.0",
                         "description": f"No Swagger/OpenAPI YAML files were found in the expected directory: {swagger_base_dir_path} (and subdirectories)"},
                "paths": {}, "components": {}
            }
            return

        aggregated_spec = {
            "openapi": "3.0.0", "info": None, "paths": {},
            "components": {"schemas": {}, "responses": {}, "parameters": {}, "examples": {},
                           "requestBodies": {}, "headers": {}, "securitySchemes": {}, "links": {}, "callbacks": {}},
            "tags": [], "servers": [], "security": [], "externalDocs": None
        }

        yaml_files.sort()
        primary_info_files_order = ["_info.yaml", "main.yaml", "openapi.yaml", "_openapi_info.yaml"]
        info_obj_found = False
        processed_primary_info_file = None

        # Attempt to load info from a primary file first
        for info_file_candidate_name in primary_info_files_order:
            # Construct full path for candidate relative to swagger_base_dir_path
            # This assumes primary info files are at the root of swagger_base_dir_path, not in subdirs for this specific check
            potential_info_file_path = os.path.join(swagger_base_dir_path, info_file_candidate_name)
            if potential_info_file_path in yaml_files: # Check if this candidate is in our found list
                try:
                    with open(potential_info_file_path, 'r', encoding='utf-8') as f:
                        content = yaml.safe_load(f)
                        if content and isinstance(content.get("info"), dict):
                            aggregated_spec["info"] = content["info"]
                            logger.info(f"Loaded primary 'info' object from: {potential_info_file_path}")
                            info_obj_found = True
                            processed_primary_info_file = potential_info_file_path
                            for key, value in content.items():
                                if key not in ["openapi", "info", "paths", "components"]:
                                    if key in ["tags", "servers"] and isinstance(value, list):
                                        aggregated_spec.setdefault(key, []).extend(value)
                                    else: aggregated_spec[key] = value
                            break
                except Exception as e:
                    logger.error(f"Error loading or parsing primary info file {potential_info_file_path}: {e}", exc_info=True)

        for yaml_file in yaml_files:
            try:
                with open(yaml_file, 'r', encoding='utf-8') as f:
                    content = yaml.safe_load(f)
                    if not content:
                        logger.warning(f"Swagger file {yaml_file} is empty or invalid. Skipping.")
                        continue

                    if yaml_file == processed_primary_info_file: # Already handled info and other top-level keys
                        if isinstance(content.get("paths"), dict):
                            deep_merge_dicts(content["paths"], aggregated_spec["paths"])
                        if isinstance(content.get("components"), dict):
                            deep_merge_dicts(content["components"], aggregated_spec["components"])
                        # Tags and servers from primary info file already added
                    else: # For other files, or if primary info file didn't set everything
                        if not info_obj_found and isinstance(content.get("info"), dict):
                            aggregated_spec["info"] = content["info"]
                            info_obj_found = True
                            logger.info(f"Loaded 'info' object from (first alphabetical): {os.path.basename(yaml_file)}")

                        if isinstance(content.get("paths"), dict):
                            deep_merge_dicts(content["paths"], aggregated_spec["paths"])
                        if isinstance(content.get("components"), dict):
                            deep_merge_dicts(content["components"], aggregated_spec["components"])
                        for key in ["tags", "servers", "security", "externalDocs"]:
                            if key in content:
                                if key in ["tags", "servers"] and isinstance(content[key], list):
                                    aggregated_spec.setdefault(key, []).extend(content[key])
                                elif key == "externalDocs" and isinstance(content[key], dict):
                                    aggregated_spec[key] = content[key]
                                elif key == "security" and isinstance(content[key], list):
                                    aggregated_spec.setdefault(key, []).extend(content[key])
                    logger.info(f"Merged content from: {os.path.basename(yaml_file)}")
            except Exception as e:
                logger.error(f"Error processing file {yaml_file}: {e}", exc_info=True)

        if aggregated_spec.get("tags"):
            unique_tags = []; seen_tag_names = set()
            for tag in aggregated_spec["tags"]:
                if isinstance(tag, dict) and tag.get("name") and tag["name"] not in seen_tag_names:
                    unique_tags.append(tag); seen_tag_names.add(tag["name"])
            aggregated_spec["tags"] = unique_tags

        if aggregated_spec.get("servers"):
            unique_servers = []; seen_server_urls = set()
            for server in aggregated_spec["servers"]:
                if isinstance(server, dict) and server.get("url") and server["url"] not in seen_server_urls:
                    unique_servers.append(server); seen_server_urls.add(server["url"])
            aggregated_spec["servers"] = unique_servers

        if not aggregated_spec.get("info"): # Ensure info always exists
            aggregated_spec["info"] = {"title": "Aggregated API Specification", "version": "1.0.0",
                                       "description": "Automatically aggregated from multiple Swagger/OpenAPI files."}
            logger.info("No 'info' object found in any Swagger file; using generic default.")

        self.api_spec = aggregated_spec
        logger.info("All Swagger files processed and merged.")

    def answer_api_question(self, question: str) -> str:
        if self.api_spec is None or not self.api_spec.get("paths"):
            logger.error("API spec is not loaded or is empty. Cannot answer question.")
            try: # Attempt one reload, just in case.
                self._load_and_parse_openapi_specs()
                if self.api_spec is None or not self.api_spec.get("paths"):
                    if self.api_spec and self.api_spec.get("info", {}).get("title") == "Error: No API Specification Found":
                        return f"Cannot answer question: {self.api_spec['info']['description']}"
                    raise RuntimeError("API specification is not loaded or is empty after reload attempt.")
            except Exception as e:
                 return f"Cannot answer question: API specification could not be loaded due to error: {e}"

        if not question:
            logger.warning("Answer_api_question called with an empty question.")
            return "Please provide a question about the API."

        try:
            spec_str = json.dumps(self.api_spec, indent=2)
            if len(spec_str) > 30000:
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
