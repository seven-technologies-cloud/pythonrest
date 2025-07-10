import yaml
import json
import os
import glob
import logging
import collections.abc
from flask import current_app # Keep for robust pathing if available

from src.e_Infra.g_McpInfra import LlmServiceBase
from src.e_Infra.g_McpInfra.PathResolver import get_swagger_config_dir # Import new utility

logger = logging.getLogger(__name__)

# PROJECT_ROOT_CONFIG_SWAGGER_DIR constant is removed, path comes from PathResolver utility

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

    # _determine_project_root() method is removed. PathResolver.get_swagger_config_dir() will be used directly.

    def _load_and_parse_openapi_specs(self):
        try:
            swagger_base_dir_path = get_swagger_config_dir() # Use the new utility
            logger.info(f"Scanning for Swagger YAML files recursively in: {swagger_base_dir_path}")
        except RuntimeError as e: # Catch error from get_swagger_config_dir if root cannot be found
            logger.critical(f"Could not determine Swagger config directory: {e}", exc_info=True)
            self.api_spec = {
                "openapi": "3.0.0",
                "info": {"title": "Error: API Specification Directory Not Found", "version": "0.0.0",
                         "description": f"Critical error: Could not determine the project's Swagger configuration directory. {e}"},
                "paths": {}, "components": {}
            }
            return


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

        for info_file_candidate_name in primary_info_files_order:
            potential_info_file_path = os.path.join(swagger_base_dir_path, info_file_candidate_name)
            if potential_info_file_path in yaml_files:
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

                    if yaml_file == processed_primary_info_file:
                        if isinstance(content.get("paths"), dict):
                            deep_merge_dicts(content["paths"], aggregated_spec["paths"])
                        if isinstance(content.get("components"), dict):
                            deep_merge_dicts(content["components"], aggregated_spec["components"])
                    else:
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

        if not aggregated_spec.get("info"):
            aggregated_spec["info"] = {"title": "Aggregated API Specification", "version": "1.0.0",
                                       "description": "Automatically aggregated from multiple Swagger/OpenAPI files."}
            logger.info("No 'info' object found in any Swagger file; using generic default.")

        self.api_spec = aggregated_spec
        logger.info("All Swagger files processed and merged.")

    def answer_api_question(self, question: str) -> str:
        if self.api_spec is None or not self.api_spec.get("paths"):
            logger.error("API spec is not loaded or is empty. Cannot answer question.")
            try:
                self._load_and_parse_openapi_specs()
                if self.api_spec is None or not self.api_spec.get("paths"):
                    if self.api_spec and self.api_spec.get("info", {}).get("title") == "Error: API Specification Found" or \
                       self.api_spec and self.api_spec.get("info", {}).get("title") == "Error: API Specification Directory Not Found": # Check for both error titles
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
