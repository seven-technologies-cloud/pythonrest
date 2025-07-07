import os
import logging

logger = logging.getLogger(__name__)

_project_root_cache = None

def get_project_root() -> str:
    """
    Determines the project root directory using a fixed relative path from this file's location.
    PathResolver.py is expected to be in ProjectRoot/src/e_Infra/g_McpInfra/
    ProjectRoot is 3 levels up from this file's directory.
    Caches the result after the first successful determination.

    Returns:
        str: The absolute path to the project root.
    """
    global _project_root_cache
    if _project_root_cache:
        return _project_root_cache

    # PathResolver.py is expected to be in ProjectRoot/src/e_Infra/g_McpInfra/
    # current_file_dir is .../ProjectRoot/src/e_Infra/g_McpInfra
    current_file_dir = os.path.abspath(os.path.dirname(__file__))

    # ../ -> .../ProjectRoot/src/e_Infra/
    # ../ -> .../ProjectRoot/src/
    # ../ -> .../ProjectRoot/
    project_root = os.path.abspath(os.path.join(current_file_dir, "..", "..", ".."))

    logger.info(f"PathResolver: Determined Project Root (fixed relative from PathResolver.py's location): {project_root}")
    _project_root_cache = project_root
    return project_root

def get_swagger_config_dir() -> str:
    """
    Returns the absolute path to the Swagger configuration directory (ProjectRoot/config/).
    """
    project_root = get_project_root()
    swagger_dir = os.path.join(project_root, "config")
    logger.debug(f"PathResolver: Swagger config directory resolved to: {swagger_dir}")
    return swagger_dir

def get_llm_runtime_config_path() -> str:
    """
    Returns the absolute path to the llm_config.json file (ProjectRoot/config/llm_config.json).
    """
    project_root = get_project_root()
    config_path = os.path.join(project_root, "config", "llm_config.json")
    logger.debug(f"PathResolver: LLM runtime config file path resolved to: {config_path}")
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
#
#         # To test, you would need to simulate the directory structure this file expects to be in.
#         # For example, create:
#         # test_project_root/
#         # |-- src/
#         # |   └── e_Infra/
#         # |       └── g_McpInfra/
#         # |           └── PathResolver.py (this file)
#         # |-- config/
#         #
#         # And then run this __main__ block from within ...g_McpInfra/
#
#     except RuntimeError as e:
#         print(f"Error: {e}")
