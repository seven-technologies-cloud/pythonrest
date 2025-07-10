import yaml
import json
import os
import glob
import logging
import collections.abc
# PathResolver will be used to get the project root and then the config/swagger directory
from src.e_Infra.g_McpInfra.PathResolver import get_swagger_config_dir

logger = logging.getLogger(__name__)

# Deep merge utility function (copied from the old ApiQueryService, can be moved to a shared util later if needed)
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
                pass # Cannot de-duplicate if items are not hashable
        else:
            destination[key] = value
    return destination

class SpecProviderService:
    """
    Service responsible for discovering, loading, parsing, and merging
    all OpenAPI/Swagger specification files from the conventional 'config/' directory
    at the project root. The aggregated specification is cached upon first load.
    """
    _cached_aggregated_spec: dict = None
    _spec_load_lock = collections.abc.Callable # Placeholder for threading.Lock, will import threading

    def __init__(self):
        if SpecProviderService._spec_load_lock is collections.abc.Callable: # Initialize lock only once
            import threading
            SpecProviderService._spec_load_lock = threading.Lock()

        self.aggregated_spec = self._get_or_load_aggregated_spec()

    def _get_or_load_aggregated_spec(self) -> dict:
        """Gets the cached spec or loads it if not already cached."""
        with SpecProviderService._spec_load_lock:
            if SpecProviderService._cached_aggregated_spec is None:
                SpecProviderService._cached_aggregated_spec = self._load_and_aggregate_specs()
            return SpecProviderService._cached_aggregated_spec

    def get_aggregated_spec(self) -> dict:
        """Returns the (cached) aggregated OpenAPI specification."""
        return self.aggregated_spec

    def get_api_base_url(self) -> str | None:
        """
        Parses the 'servers' array from the aggregated OpenAPI spec and returns the URL
        of the first server entry. Returns None if 'servers' is missing or empty.
        """
        if not self.aggregated_spec or "servers" not in self.aggregated_spec or not self.aggregated_spec["servers"]:
            logger.warning("No 'servers' array found or it is empty in the aggregated OpenAPI spec. Cannot determine base URL.")
            return None

        first_server = self.aggregated_spec["servers"][0]
        if isinstance(first_server, dict) and "url" in first_server:
            base_url = first_server["url"]
            logger.info(f"Determined API base URL from spec: {base_url}")
            return base_url

        logger.warning(f"First server entry in OpenAPI spec does not contain a 'url': {first_server}")
        return None

    def _load_and_aggregate_specs(self) -> dict:
        """
        Internal method to perform the actual loading, parsing, and merging of specs.
        This is called once and the result is cached.
        """
        logger.info("SpecProviderService: Initializing and loading/aggregating OpenAPI specs...")
        try:
            swagger_base_dir_path = get_swagger_config_dir()
            logger.info(f"Scanning for Swagger YAML files recursively in: {swagger_base_dir_path}")
        except RuntimeError as e:
            logger.critical(f"Could not determine Swagger config directory: {e}", exc_info=True)
            return {
                "openapi": "3.0.0",
                "info": {"title": "Error: API Specification Directory Not Found", "version": "0.0.0",
                         "description": f"Critical error: Could not determine the project's Swagger configuration directory. {e}"},
                "paths": {}, "components": {}
            }

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
            return {
                "openapi": "3.0.0",
                "info": {"title": "Error: No API Specification Found", "version": "0.0.0",
                         "description": f"No Swagger/OpenAPI YAML files were found in the expected directory: {swagger_base_dir_path} (and subdirectories)"},
                "paths": {}, "components": {}
            }

        # Initialize base aggregated spec
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

        logger.info("All Swagger files processed and merged successfully.")
        return aggregated_spec
