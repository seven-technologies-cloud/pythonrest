# System Imports #
import re

# Resolver Imports #
from src.e_Infra.c_Resolvers.MainConnectionResolver import *

# Handler Imports #
from src.e_Infra.a_Handlers.SystemMessagesHandler import *
from src.e_Infra.a_Handlers.ExceptionsHandler import *

# Repository Imports #
from src.d_Repository.GenericRepository import execute_sql_stored_procedure, get_result_list

# SqlAlchemy Imports #
from sqlalchemy.sql import text


# Method to validate SQL Injections
def validate_query_injection(reduced_query):
    # Iterating over list of prohibited verbs #
    for verb in black_list_sql_verbs():
        # validating verb in query #
        if verb in reduced_query:
            # Extracting sql query syntax rule verb #
            pre_index = reduced_query.index(verb) - 1
            post_index = pre_index + len(verb) + 1
            # Validating prohibit verbs in sql query syntax #
            if is_verb(reduced_query, pre_index, post_index):
                # Returning API built response #
                return build_proxy_response_insert_dumps(
                    400, {
                        get_system_message('error_message'): get_system_message('invalid_sql_injection')
                    }
                )


# Method to validate query method
def validate_query_method(reduced_query, method):
    # Iterating over list of prohibited verbs #
    for verb in black_list_method(method):
        # validating verb in query #
        if verb in reduced_query:
            # Extracting sql query syntax rule verb #
            pre_index = reduced_query.index(verb) - 1
            post_index = pre_index + len(verb) + 1
            # Validating prohibit verbs in sql query syntax #
            if is_verb(reduced_query, pre_index, post_index):
                # Returning API built response #
                return build_proxy_response_insert_dumps(
                    400, {
                        get_system_message('error_message'): get_system_message('invalid_sql_method')
                    }
                )


# Method that executes a SQL query on database
def execute_query(request_args, method):
    # Extracting SQL Query #
    query = request_args.get('HTTP_QUERY')
    # Validating if Query String Parameters is properly built #
    if query is None:
        # Returning API built response #
        return build_proxy_response_insert_dumps(
            400, {
                get_system_message('error_message'): get_system_message('malformed_input_data')
            }
        )

    # Extracting reduced query for method validation #
    reduced_query = reduce_query_statement(query)

    if method == 'PATCH' or method == 'DELETE':
        if 'where' not in reduced_query:
            return build_proxy_response_insert_dumps(
                400, {
                    get_system_message('error_message'): get_system_message('where_is_required')
                }
            )

    try:
        # Validating SQL injection in reduced query #
        query_injection_error = validate_query_injection(reduced_query)
        if query_injection_error is not None:
            return query_injection_error

        # Validating SQL verb in reduced query for HTTP method #
        query_method_error = validate_query_method(reduced_query, method)
        if query_method_error is not None:
            return query_method_error
    except:
        return handle_custom_exception(get_system_message('invalid_sql'))

    # Retrieving database connection session #
    try:
        connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    # Retrieving database engine #
    engine = connection_session.bind

    # Open engine connection with database #
    with engine.connect() as con:
        # Executing query #
        try:
            result = con.execute(text(query))

            if method == 'GET':
                pass
            else:
                con.commit()
        except Exception as e:
            if build_sql_error_table_does_not_exist(e.args[0]):
                return build_proxy_response_insert_dumps(404, {get_system_message('error_message'):
                                                               get_system_message(
                    'table_does_not_exist')})
            elif build_sql_error_invalid_syntax(e.args[0]):
                return build_proxy_response_insert_dumps(400, {get_system_message('error_message'):
                                                               get_system_message(
                    'invalid_syntax')})
            return handle_custom_exception(get_system_message('invalid_sql'))

        # Retrieving JSON if method is GET #
        if method == 'GET':
            # Retrieving result cursor #
            cursor = result.cursor

            # Retrieving JSON result #
            result = get_result_list(result, cursor)

            # Building result flask response #
            return build_proxy_response_insert_dumps(
                200, result
            )
        else:
            # Building success message flask response #
            return build_proxy_response_insert_dumps(
                200, {
                    get_system_message('message'): get_system_message('query_success')
                }
            )


# Method to verify forbidden SQL reserved words for all routes
def black_list_sql_verbs():
    # Returns black list of prohibited sql verbs #
    return ['alter', 'create', 'grant', 'revoke', 'commit', 'rollback', 'savepoint', 'drop', 'truncate']


# Method to verify forbidden SQL reserved words on different HTTP verbs
def black_list_method(method):
    # Returns black list of prohibited sql verbs for GET http method #
    if method == 'GET':
        return ['insert', 'update', 'delete']

    # Returns black list of prohibited sql verbs for POST http method #
    elif method == 'POST':
        return ['update', 'delete']

    # Returns black list of prohibited sql verbs for PATCH http method #
    elif method == 'PATCH':
        return ['insert', 'delete']

    # Returns black list of prohibited sql verbs for DELETE http method #
    elif method == 'DELETE':
        return ['insert', 'update']


# Method to transform query into acceptable queries for databases (Possible work for MySQL Only)
def reduce_query_statement(query):
    # Convert query string different quotation marks to single one #
    query = query.replace("\'", '"').replace('`', '"')
    # list of all string inside quotation marks #
    strings = re.findall('"([^"]*)"', query)
    # Iterating over list of string #
    for string in strings:
        # Removing strings from query #
        query = query.replace(f'"{string}"', "")
    # Adapting reduced query with safe spaces and returning it #
    return " " + query.replace(';', ' ; ').lower()


# Method verifies SQL rules on query
def is_verb(reduced_query, pre_index, post_index):
    # Validating SQL rule for character before found SQL verb #
    if reduced_query[pre_index].isalpha or reduced_query[pre_index].isnumeric():
        # Validating SQL rule for character after found SQL verb #
        if reduced_query[post_index].isalpha() or reduced_query[post_index].isnumeric():
            # Return False. Not SQL verb #
            return False
    # Return True. Is SQL verb #
    return True


# Method that executes a SQL stored procedure on database
def execute_post_route_sql_stored_procedure(request_headers, request_body):
    stored_procedure_name = request_headers.get('HTTP_STOREDPROCEDURE')
    stored_procedure_params = json.loads(json.dumps(request_body))
    return execute_sql_stored_procedure(stored_procedure_name, stored_procedure_params)
