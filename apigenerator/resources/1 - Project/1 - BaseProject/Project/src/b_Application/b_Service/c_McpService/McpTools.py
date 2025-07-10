import os
import json
import re
# requests import is no longer needed as extract_swagger_spec is removed
import logging
import difflib
from typing import Dict, List, Optional, Callable, Tuple, Any # Added Any
from langchain_core.tools import tool

log = logging.getLogger("mcp_tools")

# Path helpers for json_files cache are removed as the cache is no longer used by these tools.
# The aggregated_spec is now passed in directly.

# --- Tool Definitions ---

# extract_swagger_spec tool is REMOVED. Specs are now provided by SpecProviderService.

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

def find_endpoint(aggregated_spec: Dict[str, Any]) -> Callable: # Context is now the aggregated_spec
    """Factory function that returns a Langchain tool to find the most relevant endpoint for a term."""
    @tool
    def _find_endpoint_tool(search_term: str) -> Tuple[str, List[str]]:
        """
        Finds the most relevant API endpoint from the provided aggregated API specification based on a search term.
        The search looks through summaries, descriptions, paths, and parameter names.

        Args:
            search_term (str): The term or phrase to search for within the API endpoint specifications.

        Returns:
            tuple[str, list[str]]: A tuple where the first element is the path string of the best-matching endpoint
                                   (e.g., '/users/{id}'), and the second element is a list of words from the
                                   search term that were found or closely matched in the endpoint's specification.
                                   Returns an error message if no relevant endpoint is found.
        """
        if not aggregated_spec or not aggregated_spec.get("paths"):
            log.error("find_endpoint_tool: Aggregated specification is missing or has no paths.")
            return "Error: API specification not available or empty.", []

        term_words = set(re.findall(r'\b[a-zA-Z0-9_]+\b', search_term.lower()))
        best_path_str, best_score, best_match_words = None, 0, []

        # The aggregated_spec's 'paths' object contains path strings as keys
        for path_str, operations in aggregated_spec.get("paths", {}).items():
            current_path_score = 0
            current_path_matches = set()

            # Include path string itself in searchable text
            path_searchable_text = path_str.lower() + " "

            for _http_method, op_details in operations.items():
                path_searchable_text += _text_search_in_spec_data(op_details).lower() + " "

            spec_words = set(re.findall(r'\b[a-zA-Z0-9_]+\b', path_searchable_text))

            for word_to_find in term_words:
                if word_to_find in spec_words:
                    current_path_matches.add(word_to_find)
                    current_path_score += 2
                else:
                    similar_words = difflib.get_close_matches(word_to_find, list(spec_words), n=1, cutoff=0.8)
                    if similar_words:
                        current_path_matches.add(word_to_find)
                        current_path_score += 1

            if current_path_score > best_score:
                best_path_str, best_score, best_match_words = path_str, current_path_score, list(current_path_matches)

        if not best_path_str:
            log.warning(f"No relevant endpoint path found for search term: '{search_term}' in the aggregated spec.")
            return f"No relevant endpoint path found for term: '{search_term}'.", []

        log.info(f"Best endpoint path for '{search_term}': '{best_path_str}' with score {best_score} (matched: {best_match_words})")
        return best_path_str, best_match_words

    _find_endpoint_tool.name = "find_most_relevant_api_endpoint_path"
    _find_endpoint_tool.description = (
        "Searches through the aggregated API specification to find the endpoint path string (e.g., '/users/{id}') "
        "that is most relevant to the user's search_term. Considers endpoint paths, summaries, descriptions, and parameter names. "
        "Returns the best matching endpoint path string and a list of matched keywords."
    )
    return _find_endpoint_tool


def analyze_swagger(aggregated_spec: Dict[str, Any]) -> Callable: # Context is now the aggregated_spec
    """Factory function that returns a Langchain tool to analyze a specific endpoint's Swagger spec."""
    @tool
    def _analyze_swagger_tool(endpoint_path_str: str) -> Dict:
        """
        Analyzes the aggregated Swagger specification for a given endpoint_path_str and returns structured information.
        This includes available HTTP methods, summaries, descriptions, and parameters for each operation on that path.

        Args:
            endpoint_path_str (str): The specific API endpoint path string (e.g., '/users/{id}') to analyze.
                                     This should be a path known from 'find_most_relevant_api_endpoint_path'.

        Returns:
            dict: A dictionary containing structured information about the endpoint path, including its operations (methods),
                  summaries, descriptions, and parameters. Returns an error message if the endpoint path is not found.
        """
        if not aggregated_spec or not aggregated_spec.get("paths"):
            log.error("_analyze_swagger_tool: Aggregated specification is missing or has no paths.")
            return {"error": "API specification not available or empty."}

        operations_on_path = aggregated_spec.get("paths", {}).get(endpoint_path_str)
        if not operations_on_path:
            log.warning(f"No specification found for endpoint_path_str: '{endpoint_path_str}' in aggregated spec.")
            return {"error": f"No specification found for endpoint path: '{endpoint_path_str}'."}

        analysis_result = {"endpoint_path_analyzed": endpoint_path_str, "operations": {}}

        for http_method, details in operations_on_path.items():
            operation_entry = {
                "summary": details.get("summary", "No summary available."),
                "description": details.get("description", "No description available."),
                "parameters": [] # Will hold path, query, header params
            }
            # Path, query, header parameters
            for param_info in details.get("parameters", []):
                operation_entry["parameters"].append({
                    "name": param_info.get("name"),
                    "in": param_info.get("in"),
                    "description": param_info.get("description", ""),
                    "required": param_info.get("required", False),
                    "schema": param_info.get("schema", {})
                })

            # Request Body
            if details.get("requestBody"):
                body_param = {"name": "requestBody", "in": "body", "description": "Request body payload."}
                content = details["requestBody"].get("content", {})
                if "application/json" in content and "schema" in content["application/json"]:
                    body_param["schema"] = content["application/json"]["schema"]
                elif content:
                    first_content_type = list(content.keys())[0]
                    if "schema" in content[first_content_type]:
                         body_param["schema"] = content[first_content_type]["schema"]
                operation_entry["requestBody"] = body_param # Add as a separate key for clarity

            analysis_result["operations"][http_method.upper()] = operation_entry

        log.info(f"Analyzed endpoint path '{endpoint_path_str}'. Found methods: {list(analysis_result['operations'].keys())}")
        return analysis_result

    _analyze_swagger_tool.name = "analyze_endpoint_path_details"
    _analyze_swagger_tool.description = (
        "Provides a detailed breakdown of a specific API endpoint path from the aggregated specification. "
        "Input is the endpoint_path_str (e.g., '/users/{id}'). "
        "Output includes available HTTP methods for that path, and for each method: its summary, description, "
        "and parameters (path, query, header) and requestBody schema if present."
    )
    return _analyze_swagger_tool

def identify_mentioned_params(aggregated_spec: Dict[str, Any]) -> Callable: # Context is now the aggregated_spec
    """Factory function that returns a Langchain tool to identify parameters mentioned in a query."""
    @tool
    def _identify_mentioned_params_tool(endpoint_path_str: str, user_query: str) -> List[str]:
        """
        Identifies API parameters (path, query, header) for a given endpoint_path_str that are mentioned
        or seem relevant in the user_query, by checking against the aggregated API specification.
        It does not deeply analyze request body fields here.

        Args:
            endpoint_path_str (str): The specific API endpoint path (e.g., '/users/{id}') to check against.
            user_query (str): The user's natural language query or statement.

        Returns:
            list[str]: A list of parameter names (e.g., ['user_id', 'status']) found to be relevant from the user_query
                       for the specified endpoint_path. Returns an empty list if no parameters are identified or if errors occur.
        """
        if not aggregated_spec or not aggregated_spec.get("paths"):
            log.error("_identify_mentioned_params_tool: Aggregated specification is missing or has no paths.")
            return []

        operations_on_path = aggregated_spec.get("paths", {}).get(endpoint_path_str)
        if not operations_on_path:
            log.warning(f"No specification found for endpoint_path_str: '{endpoint_path_str}' in _identify_mentioned_params_tool.")
            return []

        user_query_lower = user_query.lower()
        found_params = set()

        for _http_method, op_details in operations_on_path.items():
            for param_info in op_details.get("parameters", []): # Path, query, header params
                param_name = param_info.get("name", "").lower()
                if param_name and re.search(rf"\b{re.escape(param_name)}\b", user_query_lower):
                    found_params.add(param_info.get("name")) # Add original case name

        log.info(f"For endpoint path '{endpoint_path_str}' and query '{user_query}', identified params: {list(found_params)}")
        return list(found_params)

    _identify_mentioned_params_tool.name = "identify_relevant_parameters_in_query"
    _identify_mentioned_params_tool.description = (
        "Given an endpoint_path_str and a user_query, this tool identifies which of that path's defined parameters "
        "(path, query, or header parameters; not request body fields) are mentioned or seem relevant in the user_query. "
        "Returns a list of these parameter names."
    )
    return _identify_mentioned_params_tool


def make_curl(api_base_url: Optional[str]) -> Callable: # Context is now the api_base_url string
    """Factory function that returns a Langchain tool to generate a curl command."""
    @tool
    def _make_curl_tool(endpoint_path_str: str, http_method: str, query_params_string: Optional[str] = "", headers_dict: Optional[Dict[str, str]] = None) -> str:
        """
        Generates a sample curl command for a given API endpoint_path_str, http_method, query_params_string, and headers_dict.
        Uses the API's base URL derived from its own specification if available.
        Includes common headers like 'accept: application/json' and a placeholder for 'Authorization: Bearer <API_TOKEN>'.
        For POST/PUT/PATCH, it adds a 'Content-Type: application/json' header if not provided and a placeholder for the data payload '-d '{ }''.

        Args:
            endpoint_path_str (str): The API endpoint path (e.g., /users/{id}).
            http_method (str): The HTTP method (e.g., GET, POST, PUT, DELETE).
            query_params_string (Optional[str]): A string representing query parameters, already URL-encoded if necessary
                                                 (e.g., "status=active&limit=10"). Defaults to an empty string.
            headers_dict (Optional[Dict[str, str]]): A dictionary of additional headers to include
                                                      (e.g., {"X-Custom-Header": "value"}). Defaults to None.
        Returns:
            str: A formatted string representing the generated curl command.
        """
        used_base_url = api_base_url or "<API_BASE_URL_NOT_DEFINED_IN_SPEC>"
        # Ensure endpoint_path_str starts with a slash if base_url doesn't end with one and path doesn't start with one
        if not used_base_url.endswith("/") and not endpoint_path_str.startswith("/"):
            full_url = f"{used_base_url.rstrip('/')}/{endpoint_path_str.lstrip('/')}"
        else:
            full_url = f"{used_base_url.rstrip('/')}{endpoint_path_str}"


        if query_params_string:
            query_params_string = query_params_string.lstrip('?&')
            if query_params_string:
                 full_url = f"{full_url}{'?' if '?' not in full_url else '&'}{query_params_string}"

        curl_command = f"curl -X {http_method.upper()} '{full_url}' \\"
        curl_command += f"\n     -H 'accept: application/json' \\"
        curl_command += f"\n     -H 'Authorization: Bearer <API_TOKEN>'"

        if headers_dict:
            for name, value in headers_dict.items():
                escaped_value = str(value).replace("'", "'\\''")
                curl_command += f" \\ \n     -H '{name}: {escaped_value}'"

        if http_method.upper() in ['POST', 'PUT', 'PATCH']:
            if not headers_dict or 'content-type' not in {k.lower() for k in headers_dict.keys()}:
                curl_command += " \\ \n     -H 'Content-Type: application/json'"
            curl_command += " \\ \n     -d '{ \"key\": \"value\" }'" # Slightly more useful placeholder

        log.info(f"Generated curl for {http_method.upper()} {endpoint_path_str}: {curl_command}")
        if "<API_BASE_URL_NOT_DEFINED_IN_SPEC>" in used_base_url:
            curl_command += "\n\n# Note: The API's base URL was not found in its OpenAPI specification's 'servers' object. Please replace <API_BASE_URL_NOT_DEFINED_IN_SPEC> with the actual base URL."
        return curl_command

    _make_curl_tool.name = "generate_curl_command"
    _make_curl_tool.description = (
        "Constructs a sample curl command for a specified API endpoint_path_str and http_method. "
        "The base URL is taken from the API's own specification if available. "
        "Allows optional specification of a query_params_string (e.g., 'param1=value1&param2=value2') "
        "and a headers_dict (Python dictionary for headers). "
        "Includes standard 'accept' and placeholder 'Authorization' headers. Adds 'Content-Type' and placeholder body for POST/PUT/PATCH."
    )
    return _make_curl_tool


def review_curl(api_base_url: Optional[str]) -> Callable: # Context is api_base_url
    """Factory function that returns a Langchain tool to review and 'validate' a curl command."""
    @tool
    def _review_curl_tool(endpoint_path_str: str, http_method: str, query_params_string: Optional[str] = "", headers_dict: Optional[Dict[str, str]] = None) -> str:
        """
        Reviews and 'validates' a curl command by regenerating it based on the provided components,
        using the API's base URL derived from its own specification if available.

        Args:
            endpoint_path_str (str): The API endpoint path (e.g., /users/{id}).
            http_method (str): The HTTP method (e.g., GET, POST, PUT, DELETE).
            query_params_string (Optional[str]): A string representing query parameters (e.g., "status=active&limit=10").
            headers_dict (Optional[Dict[str, str]]): A dictionary of additional headers.

        Returns:
            str: The regenerated (and thus 'reviewed') curl command string.
        """
        log.info(f"Reviewing (regenerating) curl for {http_method.upper()} {endpoint_path_str}")
        return make_curl(api_base_url)(endpoint_path_str=endpoint_path_str, http_method=http_method, query_params_string=query_params_string, headers_dict=headers_dict)

    _review_curl_tool.name = "review_and_regenerate_curl_command"
    _review_curl_tool.description = (
         "Takes components of an API request (endpoint_path_str, http_method, optional query_params_string, optional headers_dict) "
         "and regenerates a standardized curl command using the API's own base URL from its spec. Useful for validating or formatting a user's intended API call."
    )
    return _review_curl_tool
