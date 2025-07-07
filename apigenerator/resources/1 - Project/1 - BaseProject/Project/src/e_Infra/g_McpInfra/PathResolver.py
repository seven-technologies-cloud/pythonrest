import os
import logging

logger = logging.getLogger(__name__)

_project_root_cache = None

def get_project_root() -> str:
    """
    Robustly determines the project root directory.
    The project root is identified as the first parent directory (starting from this file's dir)
    that contains both 'src' and 'config' as subdirectories.
    Caches the result after the first successful determination.

    Returns:
        str: The absolute path to the project root.

    Raises:
        RuntimeError: If the project root cannot be determined after traversing a reasonable number of parent directories.
    """
    global _project_root_cache
    if _project_root_cache:
        return _project_root_cache

    current_path = os.path.abspath(os.path.dirname(__file__)) # Directory of PathResolver.py

    # PathResolver.py is in src/e_Infra/g_McpInfra/
    # We expect ProjectRoot/src/ and ProjectRoot/config/
    # So, from PathResolver.py, ProjectRoot is 3 levels up.
    # We'll search a bit more just in case of slight variations or future refactoring.
    max_levels_up = 7

    for _ in range(max_levels_up):
        # Check if 'src' and 'config' directories exist in the current_path
        # This assumes 'src' and 'config' are direct children of the project root.
        # The path we are looking for is the one that CONTAINS 'src' and 'config'
        # So if current_path is '.../Project/', then os.path.join(current_path, 'src') exists.

        # If PathResolver.py is at .../Project/src/e_Infra/g_McpInfra/PathResolver.py
        # 1st current_path = .../Project/src/e_Infra/g_McpInfra
        # 2nd current_path (parent) = .../Project/src/e_Infra
        # 3rd current_path (parent) = .../Project/src
        # 4th current_path (parent) = .../Project  <- This is the one we want.
        # At this 4th level, os.path.join(current_path, "src") and os.path.join(current_path, "config") should exist.

        potential_src_path = os.path.join(current_path, "src")
        potential_config_path = os.path.join(current_path, "config")

        if os.path.isdir(potential_src_path) and os.path.isdir(potential_config_path):
            logger.info(f"Project root determined: {current_path} (found 'src' and 'config' subdirectories).")
            _project_root_cache = current_path
            return current_path

        parent_path = os.path.dirname(current_path)
        if parent_path == current_path: # Reached filesystem root
            break
        current_path = parent_path

    logger.critical("Could not determine project root. Searched for a directory containing both 'src' and 'config' subdirectories.")
    raise RuntimeError("Could not determine project root. Ensure 'src' and 'config' folders exist at the project root level relative to PathResolver.py's expected location.")

def get_swagger_config_dir() -> str:
    """
    Returns the absolute path to the Swagger configuration directory (ProjectRoot/config/).
    """
    project_root = get_project_root()
    swagger_dir = os.path.join(project_root, "config")
    # logger.debug(f"Swagger config directory resolved to: {swagger_dir}")
    return swagger_dir

def get_llm_runtime_config_path() -> str:
    """
    Returns the absolute path to the llm_config.json file (ProjectRoot/config/llm_config.json).
    """
    project_root = get_project_root()
    config_path = os.path.join(project_root, "config", "llm_config.json")
    # logger.debug(f"LLM runtime config file path resolved to: {config_path}")
    return config_path

# Example usage (primarily for testing PathResolver.py itself)
# if __name__ == '__main__':
#     logging.basicConfig(level=logging.INFO)
#     try:
#         root = get_project_root()
#         print(f"Determined Project Root: {root}")
#         swagger_dir = get_swagger_config_dir()
#         print(f"Determined Swagger Config Dir: {swagger_dir}")
#         llm_json_path = get_llm_runtime_config_path()
#         print(f"Determined LLM Runtime Config Path: {llm_json_path}")
#     except RuntimeError as e:
#         print(f"Error: {e}")
