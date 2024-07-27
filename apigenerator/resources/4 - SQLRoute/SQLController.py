# Flask Imports #
from src.e_Infra.b_Builders.FlaskBuilder import *

# Service Layer Imports #
from src.b_Application.b_Service.b_Custom.SQLService import *


@app_handler.route('/sql', methods=['GET'])
def sql_direct_get_route():
    # Routing request to /sql many methods #
    result = execute_query(
        {'HTTP_QUERY': request.environ.get('HTTP_QUERY')}, request.method)
    return result


@app_handler.route('/sql', methods=['POST', 'PATCH'])
def sql_direct_post_patch_route():
    # Routing request to /sql many methods #
    result = execute_query(
        {'HTTP_QUERY': request.environ.get('HTTP_QUERY')}, request.method)
    return result


@app_handler.route('/sql', methods=['DELETE'])
def sql_direct_route():
    # Routing request to /sql many methods #
    result = execute_query(
        {'HTTP_QUERY': request.environ.get('HTTP_QUERY')}, request.method)
    return result


@app_handler.route('/sql/storedprocedure', methods=['POST'])
def sql_stored_procedure_post_route():
    result = execute_post_route_sql_stored_procedure(
        request.environ, request.json)
    return result
