import os
import json
import re
import requests
import logging
import difflib
from typing import Dict, List, Optional, Callable, Tuple # Corrected typing for Tuple
from langchain_core.tools import tool
# langchain_ollama is not needed as Ollama support is removed.

# Configure logging for this module
# Using a generic logger name that can be configured by the app's logging setup
log = logging.getLogger("mcp_tools") # Changed from __name__ to be more specific if imported
# BasicConfig should ideally be called once at application startup, not in every module.
# Assuming it might be called in EnvironmentVariables.py or app.py.
# If not, uncommenting this might be needed for standalone tool testing:
# logging.basicConfig(level=logging.INFO)

# --- Path Helper for json_files cache ---
_PROJECT_ROOT_CACHE = None

def _get_project_root_for_tools() -> str:
    """
    Determines the project root for storing/accessing json_files.
    Assumes McpTools.py is at .../src/b_Application/b_Service/c_McpService/McpTools.py
    Project root is considered 4 levels up from this file's directory.
    Caches the result.
    """
    global _PROJECT_ROOT_CACHE
    if _PROJECT_ROOT_CACHE:
        return _PROJECT_ROOT_CACHE

    # Path of McpTools.py: .../src/b_Application/b_Service/c_McpService/McpTools.py
    # We want to reach .../ (Project Root)
    # c_McpService -> b_Service -> b_Application -> src -> ProjectRoot
    current_file_dir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", "..", ".."))
    log.info(f"McpTools: Determined project root for json_files: {project_root}")
    _PROJECT_ROOT_CACHE = project_root
    return project_root

def _get_json_cache_path(filename: str = "all_endpoints.json") -> str:
    """Returns the absolute path to the cached JSON file in 'json_files' at project root."""
    project_root = _get_project_root_for_tools()
    cache_dir = os.path.join(project_root, "json_files")
    return os.path.join(cache_dir, filename)

# --- Tool Definitions ---

def extract_swagger_spec(context: Dict) -> Callable:
    """
    Factory function that returns a Langchain tool to extract Swagger JSON specs.
    The tool fetches specs from URLs derived from base_url and endpoints in the context,
    then saves them to a local JSON file.
    """
    @tool
    def _extract_swagger_spec_tool() -> str:
        """
        Extracts Swagger JSON specifications from configured endpoints and saves them
        to a local cache file ('json_files/all_endpoints.json').
        This tool should typically be called once to populate the cache if it's stale or missing.
        Returns a status message.
        """
        base_url = context.get("base_url")
        endpoints = context.get("endpoints")

        if not base_url or not isinstance(endpoints, list):
            log.error("extract_swagger_spec_tool: 'base_url' or 'endpoints' missing or invalid in context.")
            return "Error: base_url and endpoints list must be provided in the context."

        all_specs: Dict[str, Dict] = {}
        log.info(f"extract_swagger_spec_tool: Starting extraction for base_url: {base_url}, endpoints: {endpoints}")

        for endpoint_path in endpoints:
            # Ensure endpoint_path starts with a slash if not already
            if not endpoint_path.startswith("/"):
                endpoint_path = "/" + endpoint_path

            # Construct URL, assuming /swagger prefix is part of the convention
            # If swagger is already in base_url or endpoint_path, adjust accordingly
            url = f"{base_url.rstrip('/')}/swagger{endpoint_path.rstrip('/')}" # Ensure single slash

            log.info(f"extract_swagger_spec_tool: Fetching spec from {url}")
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                html_content = response.text

                # Regex to find the SwaggerUIBundle spec object
                # This regex is specific and might need adjustment if the HTML structure of Swagger UI changes.
                match = re.search(r"SwaggerUIBundle\(\s*{\s*spec:\s*(\{.*?\})\s*,\s*dom_id:", html_content, re.DOTALL | re.IGNORECASE)

                if match:
                    spec_json_str = match.group(1)
                    # Further cleaning: a common issue is trailing commas in the JSON object within the JS
                    spec_json_str = re.sub(r',\s*\}', '}', spec_json_str)
                    spec_json_str = re.sub(r',\s*\]', ']', spec_json_str)
                    try:
                        spec_data = json.loads(spec_json_str)
                        all_specs[endpoint_path] = spec_data
                        log.info(f"Successfully extracted spec for endpoint: {endpoint_path}")
                    except json.JSONDecodeError as json_e:
                        log.error(f"JSONDecodeError for endpoint {endpoint_path} at {url}: {json_e}. Content snippet: {spec_json_str[:500]}")
                        all_specs[endpoint_path] = {"error": f"Failed to parse JSON: {json_e}"}
                else:
                    log.warning(f"Could not find Swagger spec JSON in HTML from {url}. Pattern 'SwaggerUIBundle(... spec: ...)' not found.")
                    all_specs[endpoint_path] = {"error": "Spec pattern not found in HTML content"}
            except requests.exceptions.RequestException as req_e:
                log.error(f"RequestException for endpoint {endpoint_path} at {url}: {req_e}")
                all_specs[endpoint_path] = {"error": f"Request failed: {req_e}"}
            except Exception as e:
                log.error(f"Generic Exception for endpoint {endpoint_path} at {url}: {e}", exc_info=True)
                all_specs[endpoint_path] = {"error": f"An unexpected error occurred: {str(e)}"}

        cache_file_path = _get_json_cache_path()
        cache_dir = os.path.dirname(cache_file_path)
        try:
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file_path, "w", encoding="utf-8") as f:
                json.dump(all_specs, f, indent=2, ensure_ascii=False)
            log.info(f"All Swagger specs saved to {cache_file_path}")
            return f"Swagger specifications for {len(endpoints)} endpoint(s) processed and saved to cache."
        except IOError as io_e:
            log.error(f"IOError saving specs to {cache_file_path}: {io_e}")
            return f"Error saving Swagger specs: {io_e}"
        except Exception as e:
            log.error(f"Unexpected error saving specs to {cache_file_path}: {e}", exc_info=True)
            return f"Unexpected error saving Swagger specs: {str(e)}"

    _extract_swagger_spec_tool.name = "extract_swagger_specifications" # Tool name for Langchain
    _extract_swagger_spec_tool.description = (
        "Fetches Swagger JSON specifications from all configured API endpoints "
        "(derived from a base URL and a list of endpoint paths). "
        "Saves the aggregated specifications into a local JSON file cache ('json_files/all_endpoints.json'). "
        "This tool should be called if the API specification cache is suspected to be stale or is missing, "
        "or to initially populate it. It does not take any arguments."
    )
    return _extract_swagger_spec_tool

def _text_search_in_spec_data(spec_data_item: any) -> str:
    """Helper function to recursively extract all string values from spec data for text search."""
    text_parts = []
    if isinstance(spec_data_item, dict):
        for value in spec_data_item.values():
            text_parts.append(_text_search_in_spec_data(value))
    elif isinstance(spec_data_item, list):
        for item in spec_data_item:
            text_parts.append(_text_search_in_spec_data(item))
    elif isinstance(spec_data_item, str):
        text_parts.append(spec_data_item)
    return " ".join(text_parts)

def find_endpoint(context: Dict) -> Callable:
    """Factory function that returns a Langchain tool to find the most relevant endpoint for a term."""
    @tool
    def _find_endpoint_tool(search_term: str) -> Tuple[str, List[str]]:
        """
        Finds the most relevant API endpoint from the cached Swagger specifications based on a search term.
        The search looks through summaries, descriptions, paths, and parameter names.

        Args:
            search_term (str): The term or phrase to search for within the API endpoint specifications.

        Returns:
            tuple[str, list[str]]: A tuple where the first element is the path of the best-matching endpoint
                                   (e.g., '/users/{id}'), and the second element is a list of words from the
                                   search term that were found or closely matched in the endpoint's specification.
                                   Returns an error message if the cache file is missing.
        """
        cache_file_path = _get_json_cache_path()
        if not os.path.exists(cache_file_path):
            log.error(f"find_endpoint_tool: Cache file {cache_file_path} not found. Run 'extract_swagger_specifications' tool first.")
            return "Error: Swagger specification cache not found. Please run the 'extract_swagger_specifications' tool first.", []

        with open(cache_file_path, "r", encoding="utf-8") as f:
            swagger_specs = json.load(f)

        term_words = set(re.findall(r'\b[a-zA-Z0-9_]+\b', search_term.lower())) # Include underscore
        best_ep, best_score, best_match_words = None, 0, []

        for ep_path, spec_content in swagger_specs.items():
            if "error" in spec_content:
                log.warning(f"Skipping endpoint '{ep_path}' due to previous extraction error: {spec_content['error']}")
                continue

            # Build a searchable text corpus from the spec content
            searchable_text = _text_search_in_spec_data(spec_content).lower()
            spec_words = set(re.findall(r'\b[a-zA-Z0-9_]+\b', searchable_text)) # Include underscore

            current_matches = set()
            current_score = 0
            for word_to_find in term_words:
                if word_to_find in spec_words:
                    current_matches.add(word_to_find)
                    current_score += 2 # Exact match bonus
                else:
                    # Use difflib for close matches if exact match fails
                    # Consider a higher cutoff for more relevance
                    similar_words = difflib.get_close_matches(word_to_find, list(spec_words), n=1, cutoff=0.8)
                    if similar_words:
                        current_matches.add(word_to_find) # Add the original search term word
                        current_score += 1 # Partial match score

            if current_score > best_score:
                best_ep, best_score, best_match_words = ep_path, current_score, list(current_matches)

        if not best_ep:
            log.warning(f"No relevant endpoint found for search term: '{search_term}'")
            return f"No relevant endpoint found for term: '{search_term}'. Try a different term or ensure specs are extracted.", []

        log.info(f"Best endpoint for '{search_term}': '{best_ep}' with score {best_score} (matched: {best_match_words})")
        return best_ep, best_match_words

    _find_endpoint_tool.name = "find_most_relevant_api_endpoint"
    _find_endpoint_tool.description = (
        "Searches through cached API specifications to find the endpoint path that is most relevant to the user's search_term. "
        "It considers endpoint paths, summaries, descriptions, and parameter names. "
        "Returns the best matching endpoint path and a list of matched keywords from the search term."
    )
    return _find_endpoint_tool


def analyze_swagger(context: Dict) -> Callable:
    """Factory function that returns a Langchain tool to analyze a specific endpoint's Swagger spec."""
    @tool
    def _analyze_swagger_tool(endpoint_path: str) -> Dict:
        """
        Analyzes the cached Swagger specification for a given endpoint_path and returns structured information.
        This includes available HTTP methods, summaries, descriptions, and parameters for each operation.

        Args:
            endpoint_path (str): The specific API endpoint path (e.g., '/users/{id}') to analyze.
                                 This should be a path known from 'find_most_relevant_api_endpoint' or similar.

        Returns:
            dict: A dictionary containing structured information about the endpoint, including its operations (methods),
                  summaries, descriptions, and parameters. Returns an error message if the cache or endpoint is not found.
        """
        cache_file_path = _get_json_cache_path()
        if not os.path.exists(cache_file_path):
            log.error(f"_analyze_swagger_tool: Cache file {cache_file_path} not found. Run 'extract_swagger_specifications' tool first.")
            return {"error": "Swagger specification cache not found. Please run the 'extract_swagger_specifications' tool first."}

        with open(cache_file_path, "r", encoding="utf-8") as f:
            all_specs = json.load(f)

        endpoint_spec_data = all_specs.get(endpoint_path)
        if not endpoint_spec_data or "error" in endpoint_spec_data:
            log.warning(f"No valid specification found for endpoint_path: '{endpoint_path}' in cache.")
            return {"error": f"No valid specification found for endpoint: '{endpoint_path}'. It might not exist or failed during extraction."}

        analysis_result = {"base_endpoint_path": endpoint_path, "operations": {}}

        for path_key_in_spec, methods_dict in endpoint_spec_data.get('paths', {}).items():
            # path_key_in_spec is the actual path string like "/items/{itemId}"
            # It should generally match or be related to endpoint_path for single endpoint specs
            # If all_endpoints.json stores specs keyed by their main path, this loop might just run once.
            analysis_result["operations"][path_key_in_spec] = {}
            for http_method, details in methods_dict.items():
                operation_entry = {
                    "summary": details.get("summary", "No summary available."),
                    "description": details.get("description", "No description available."),
                    "parameters": []
                }
                for param_info in details.get("parameters", []):
                    operation_entry["parameters"].append({
                        "name": param_info.get("name"),
                        "in": param_info.get("in"), # e.g., "path", "query", "header", "cookie"
                        "description": param_info.get("description", ""),
                        "required": param_info.get("required", False),
                        "schema": param_info.get("schema", {}) # Type, format, etc.
                    })

                if details.get("requestBody"):
                    # Simplified representation for requestBody
                    body_param = {"name": "requestBody", "in": "body", "description": "Request body payload."}
                    # Try to get more schema info if available
                    content = details["requestBody"].get("content", {})
                    if "application/json" in content and "schema" in content["application/json"]:
                        body_param["schema"] = content["application/json"]["schema"]
                    elif content: # Take first available content type
                        first_content_type = list(content.keys())[0]
                        if "schema" in content[first_content_type]:
                             body_param["schema"] = content[first_content_type]["schema"]
                    operation_entry["parameters"].append(body_param)

                analysis_result["operations"][path_key_in_spec][http_method.upper()] = operation_entry

        log.info(f"Analyzed endpoint '{endpoint_path}'. Found operations: {list(analysis_result['operations'].keys())}")
        return analysis_result

    _analyze_swagger_tool.name = "analyze_endpoint_specification"
    _analyze_swagger_tool.description = (
        "Provides a detailed breakdown of a specific API endpoint's specification from the cache. "
        "Input is the endpoint_path (e.g., '/users/{id}'). "
        "Output includes available HTTP methods, summaries, descriptions, and parameters (path, query, header, body) for each operation on that endpoint."
    )
    return _analyze_swagger_tool

def identify_mentioned_params(context: Dict) -> Callable:
    """Factory function that returns a Langchain tool to identify parameters mentioned in a query."""
    @tool
    def _identify_mentioned_params_tool(endpoint_path: str, user_query: str) -> List[str]:
        """
        Identifies API parameters (path, query, header) for a given endpoint_path that are mentioned
        or seem relevant in the user_query. It does not consider request body parameters here.

        Args:
            endpoint_path (str): The specific API endpoint path (e.g., '/users/{id}') to check against.
            user_query (str): The user's natural language query or statement.

        Returns:
            list[str]: A list of parameter names (e.g., ['user_id', 'status']) found to be relevant from the user_query
                       for the specified endpoint_path. Returns an empty list if no parameters are identified or if errors occur.
        """
        cache_file_path = _get_json_cache_path()
        if not os.path.exists(cache_file_path):
            log.error(f"_identify_mentioned_params_tool: Cache file {cache_file_path} not found.")
            return [] # Return empty list on error as per original snippet's intent

        with open(cache_file_path, "r", encoding="utf-8") as f:
            all_specs = json.load(f)

        endpoint_spec_data = all_specs.get(endpoint_path)
        if not endpoint_spec_data or "error" in endpoint_spec_data:
            log.warning(f"No valid specification found for endpoint_path: '{endpoint_path}' in _identify_mentioned_params_tool.")
            return []

        user_query_lower = user_query.lower()
        found_params = set()

        for _path_key_in_spec, methods_dict in endpoint_spec_data.get('paths', {}).items():
            for _http_method, details in methods_dict.items():
                for param_info in details.get("parameters", []):
                    param_name = param_info.get("name", "").lower()
                    # Check if param_name is not empty and is found as a whole word in the user_query
                    if param_name and re.search(rf"\b{re.escape(param_name)}\b", user_query_lower):
                        found_params.add(param_info.get("name")) # Add original case name

        log.info(f"For endpoint '{endpoint_path}' and query '{user_query}', identified params: {list(found_params)}")
        return list(found_params)

    _identify_mentioned_params_tool.name = "identify_relevant_parameters_in_query"
    _identify_mentioned_params_tool.description = (
        "Given an endpoint_path and a user_query, this tool identifies which of the endpoint's defined parameters "
        "(path, query, or header parameters; not request body fields) are mentioned or seem relevant in the user_query. "
        "Returns a list of these parameter names."
    )
    return _identify_mentioned_params_tool


def make_curl(context: Dict) -> Callable:
    """Factory function that returns a Langchain tool to generate a curl command."""
    @tool
    def _make_curl_tool(endpoint_path: str, http_method: str, query_params_string: Optional[str] = "", headers_dict: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a sample curl command for a given API endpoint_path, http_method, query_params_string, and headers_dict.
        Includes common headers like 'accept: application/json' and a placeholder for 'Authorization: Bearer <API_TOKEN>'.
        For POST/PUT/PATCH, it adds a 'Content-Type: application/json' header if not provided and a placeholder for the data payload '-d '{ }''.

        Args:
            endpoint_path (str): The API endpoint path (e.g., /users/{id}).
            http_method (str): The HTTP method (e.g., GET, POST, PUT, DELETE).
            query_params_string (Optional[str]): A string representing query parameters, already URL-encoded if necessary
                                                 (e.g., "status=active&limit=10"). Defaults to an empty string.
            headers_dict (Optional[Dict[str, str]]): A dictionary of additional headers to include
                                                      (e.g., {"X-Custom-Header": "value"}). Defaults to None.
        Returns:
            str: A formatted string representing the generated curl command.
        """
        base_url = context.get("base_url", "").rstrip('/')
        full_url = f"{base_url}{endpoint_path}"

        if query_params_string:
            separator = "&" if "?" in full_url else "?" # This logic is flawed if query_params_string itself contains '?'
            # Better: ensure query_params_string does not start with '?' or '&'
            query_params_string = query_params_string.lstrip('?&')
            if query_params_string: # Only add if non-empty after stripping
                 full_url = f"{full_url}{'?' if '?' not in full_url else '&'}{query_params_string}"


        curl_command = f"curl -X {http_method.upper()} '{full_url}' \\"

        # Standard headers
        curl_command += f"\n     -H 'accept: application/json' \\"
        curl_command += f"\n     -H 'Authorization: Bearer <API_TOKEN>'" # Placeholder token

        # User-provided headers
        if headers_dict:
            for name, value in headers_dict.items():
                # Basic escaping for single quotes in header values
                escaped_value = str(value).replace("'", "'\\''")
                curl_command += f" \\ \n     -H '{name}: {escaped_value}'"

        # Handle body for relevant methods
        if http_method.upper() in ['POST', 'PUT', 'PATCH']:
            # Add Content-Type if not already in user-provided headers
            if not headers_dict or 'content-type' not in {k.lower() for k in headers_dict.keys()}:
                curl_command += " \\ \n     -H 'Content-Type: application/json'"
            curl_command += " \\ \n     -d '{ }'" # Placeholder JSON body

        log.info(f"Generated curl for {http_method.upper()} {endpoint_path}: {curl_command}")
        return curl_command

    _make_curl_tool.name = "generate_curl_command"
    _make_curl_tool.description = (
        "Constructs a sample curl command for a specified API endpoint_path and http_method. "
        "Allows optional specification of a query_params_string (e.g., 'param1=value1&param2=value2') "
        "and a headers_dict (Python dictionary for headers). "
        "Includes standard 'accept' and placeholder 'Authorization' headers. Adds 'Content-Type' and placeholder body for POST/PUT/PATCH."
    )
    return _make_curl_tool


def review_curl(context: Dict) -> Callable: # Kept as per user's file, though it just calls make_curl
    """
    Factory function that returns a Langchain tool to review and validate a curl command.
    Currently, this tool regenerates the command using make_curl for simplicity.
    """
    @tool
    def _review_curl_tool(endpoint_path: str, http_method: str, query_params_string: Optional[str] = "", headers_dict: Optional[Dict[str, str]] = None) -> str:
        """
        Reviews and 'validates' a curl command by regenerating it based on the provided components.
        This tool essentially calls 'generate_curl_command' with the same arguments to produce a standardized version.

        Args:
            endpoint_path (str): The API endpoint path (e.g., /users/{id}).
            http_method (str): The HTTP method (e.g., GET, POST, PUT, DELETE).
            query_params_string (Optional[str]): A string representing query parameters (e.g., "status=active&limit=10").
            headers_dict (Optional[Dict[str, str]]): A dictionary of additional headers.

        Returns:
            str: The regenerated (and thus 'reviewed') curl command string.
        """
        log.info(f"Reviewing (regenerating) curl for {http_method.upper()} {endpoint_path}")
        # This tool currently just regenerates the command. True validation would be more complex.
        return make_curl(context)(endpoint_path=endpoint_path, http_method=http_method, query_params_string=query_params_string, headers_dict=headers_dict)

    _review_curl_tool.name = "review_and_regenerate_curl_command"
    _review_curl_tool.description = (
         "Takes components of an API request (endpoint_path, http_method, optional query_params_string, optional headers_dict) "
         "and regenerates a standardized curl command. Useful for validating or formatting a user's intended API call."
    )
    return _review_curl_tool
