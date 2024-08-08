# Repository Imports #
from src.d_Repository.b_Transactions.GenericDatabaseTransaction import *

# Validator Imports #
from src.e_Infra.d_Validators.SqlAlchemyDataValidator import validate_request_data_object, validate_header_args
from src.e_Infra.d_Validators.RequestJSONValidator import *

# Handler Imports #
from src.e_Infra.a_Handlers.SystemMessagesHandler import *
from src.e_Infra.a_Handlers.ExceptionsHandler import *

# Builder Imports #
from src.e_Infra.b_Builders.DomainObjectBuilder import build_domain_object_from_dict, build_object_error_message
from src.e_Infra.b_Builders.ProxyResponseBuilder import *

# Resolver Imports #
from src.e_Infra.c_Resolvers.MainConnectionResolver import *

# SqlAlchemy Imports #
from sqlalchemy.sql import text


# Method retrieves an entity set by its given 'request_args' parameters #
def get_all(declarative_meta, request_args, header_args):
    try:
        cast_request_args(
            request_args, declarative_meta
        )

        cast_headers_args(
            header_args
        )

        validate_request_data_object(
            declarative_meta, request_args
        )

        validate_header_args(
            declarative_meta, header_args
        )

    except Exception as e:
        return build_proxy_response_insert_dumps(
            400, {get_system_message('error_message'): e.args[0].replace(
                '__init__()', declarative_meta.__table__.name
            )}
        )

    # Connecting to database #
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        # Retrieving results #
        result_set = select_all_objects(
            declarative_meta, request_args, main_connection_session, header_args
        )
        if result_set == '[]':
            # Return items not found when list is empty #
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): get_system_message('get_no_items_found')}
            )
        else:
            # Otherwise, return API built response with items #
            return build_proxy_response(
                200, result_set
            )
    except Exception as e:
        return handle_custom_exception(e)


# Method retrieves a given entity by its given 'id' and 'request_args' parameters #
def get_by_id(declarative_meta, id_value_list, request_args, id_name_list, header_args):
    try:
        cast_request_args(
            request_args, declarative_meta
        )

        cast_headers_args(
            header_args
        )

        validate_request_data_object(
            declarative_meta, request_args
        )

        validate_header_args(
            declarative_meta, header_args
        )

    except Exception as e:
        return build_proxy_response_insert_dumps(
            400, {get_system_message('error_message'): e.args[0].replace(
                '__init__()', declarative_meta.__table__.name
            )}
        )

    # Connecting to database #
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        # Retrieving results #
        result_set = select_object_by_id(
            declarative_meta, id_value_list, id_name_list, request_args, main_connection_session, header_args
        )

        # Returning API built response #
        if result_set == '[]':
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): f"Object with given parameter '{id_value_list[0]}' "
                                                           f"not found."}
            )
        else:
            return build_proxy_response(200, result_set)

    except Exception as e:
        return handle_custom_exception(e)


# Method deletes a given entity by its given 'id' #
def delete_by_id(declarative_meta, id_value_list, id_name_list):
    # Connecting to database #
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        result = delete_object_by_id(
            declarative_meta, id_value_list, id_name_list, main_connection_session
        )
        if result > 0:
            # Returning API built response  #
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message(
                    'object_deleted_success')}
            )
        else:
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): f"Object with given parameter '{id_value_list[0]}' "
                                                           f"not found."}
            )
    # Treating exception #
    except Exception as e:
        return handle_custom_exception(e)


# Method inserts or updates a given entity #
def put_object_set(request_data, declarative_meta, id_name_list):
    # Setting default error status code #
    error_status_code = 400

    # Connecting to database #
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response
    try:
        # Initializing error message list #
        error_message_list = get_system_empty_list()

        # Casting request_data param into a list if not already #
        if type(request_data) != list:
            request_data = [request_data]

        # Iterating over objects in request_data param #
        for request_data_object in request_data:

            # Validating request data object #
            try:
                validate_request_data_object(
                    declarative_meta, request_data_object
                )
            except Exception as e:
                # Appending error message #
                error_message_list.append(
                    build_object_error_message(
                        request_data_object, e
                    )
                )
                error_status_code = 406
                continue

            if request.method == 'POST':
                # Executing insert block #
                insert_result = insert_object_from_set(
                    declarative_meta, request_data_object, main_connection_session
                )

                # Validating insert results #
                if insert_result != get_system_null():
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, insert_result
                        )
                    )

                    for error in insert_result:
                        if 'Duplicate entry' in error:
                            error_status_code = 409
                        if 'cannot be null' in error:
                            error_status_code = 406
                    continue

            if request.method == 'PATCH':
                missing_pk = next(
                    (
                        True for id_object in id_name_list if id_object not in request_data_object
                    ),
                    False
                )
                if missing_pk:
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, get_system_message(
                                'dict_from_body_no_pk_patch')
                        )
                    )
                    error_status_code = 406
                    continue
                pk_only = next(
                    (
                        False for key in request_data_object if key not in id_name_list
                    ),
                    True
                )
                if pk_only:
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, get_system_message(
                                'cannot_update_with_id_only')
                        )
                    )
                    error_status_code = 406
                    continue
                # Executing update block #
                update_result = update_object_from_set(
                    declarative_meta, request_data_object, id_name_list, main_connection_session
                )
                # Validating update results #
                if type(update_result) != int:
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, update_result
                        )
                    )
                if update_result == 0:
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, get_system_message(
                                'patch_no_items_found')
                        )
                    )
                    error_status_code = 404
                    continue
            if request.method == 'PUT':
                missing_pk = next(
                    (
                        True for id_object in id_name_list if id_object not in request_data_object
                    ),
                    False
                )
                if missing_pk:
                    # Executing insert block #
                    insert_result = insert_object_from_set(
                        declarative_meta, request_data_object, main_connection_session
                    )
                    # Validating insert results #
                    if insert_result != get_system_null():
                        error_message_list.append(
                            build_object_error_message(
                                request_data_object, insert_result
                            )
                        )
                        for error in insert_result:
                            if 'cannot be null' in error:
                                error_status_code = 406
                    continue
                pk_only = next(
                    (
                        False for key in request_data_object if key not in id_name_list
                    ),
                    True
                )
                if pk_only:
                    # Executing insert block #
                    insert_result = insert_object_from_set(
                        declarative_meta, request_data_object, main_connection_session
                    )

                    # Validating insert results #
                    if insert_result != get_system_null():
                        error_message_list.append(
                            build_object_error_message(
                                request_data_object, insert_result
                            )
                        )
                        for error in insert_result:
                            if 'cannot be null' in error:
                                error_status_code = 406
                    continue
                # Executing update block #
                update_result = update_object_from_set(
                    declarative_meta, request_data_object, id_name_list, main_connection_session
                )

                # Validating update results #
                if type(update_result) != int:
                    error_message_list.append(
                        build_object_error_message(
                            request_data_object, update_result
                        )
                    )
                    continue
                if update_result == 0:
                    # Executing insert block #
                    insert_result = insert_object_from_set(
                        declarative_meta, request_data_object, main_connection_session
                    )

                    # Validating insert results #
                    if insert_result != get_system_null():
                        error_message_list.append(
                            build_object_error_message(
                                request_data_object, insert_result
                            )
                        )
                    continue

        # Returning full success API built response #
        if error_message_list == get_system_empty_list():
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message(
                    'object_set_persisted_success')}
            )

        # Checking if there is more than one error #
        if len(error_message_list) > 1:
            error_status_code = 400

        # Returning error list as an API built response #
        return build_proxy_response_insert_dumps_error_list(
            error_status_code, error_message_list
        )

    # Treating exception #
    except Exception as e:
        return handle_custom_exception(e)


# Method inserts a given entity set #
def insert_object_set(request_data, declarative_meta):
    # Returning definitions from put method #
    return put_object_set(
        request_data, declarative_meta, get_system_null()
    )


# Method updates a given entity set #
def update_object_set(request_data, declarative_meta, id_name_list):
    # Returning definitions from put method #
    return put_object_set(
        request_data, declarative_meta, id_name_list
    )


# Method inserts a given entity or return its error in case of failure #
def insert_object_from_set(declarative_meta, request_data_object, main_connection_session):
    try:
        # Filling guid in primary key when not available #
        auto_fill_guid_in_request_body(
            declarative_meta, request_data_object
        )
        # Creating object for insert #
        transact_object = build_domain_object_from_dict(
            declarative_meta, request_data_object
        )
        # Result for insert transaction method #
        result = insert_object(
            transact_object, main_connection_session
        )
    except Exception as e:
        # Returning custom handle exception for repository transactions #
        return handle_repository_exception(e)

    # Returning built error message if insert not successful #
    if result != get_system_null():
        return result

    # Returning system null indicating success #
    return get_system_null()


# Method updates a given entity or return its error in case of failure #
def update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session):
    # Executing update block #
    try:
        # Filling put object without transact_object (update) #
        result = update_object(
            declarative_meta, request_data_object, id_name_list, main_connection_session
        )
    except Exception as e:
        # Returning custom handle exception for repository transactions #
        return handle_repository_exception(e)

    # Returning update result #
    return result

# Deletes a given entity by providing all fields of the entity table #


def delete_set_by_full_match(request_data, declarative_meta):
    # Setting Default Error Status Code #
    error_status_code = 400

    # Connecting to database #
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response
    try:
        # Initializing error message list #
        error_message_list = get_system_empty_list()

        # Casting request_data param into a list if not already #
        if type(request_data) != list:
            request_data = [request_data]

        # Iterating over objects in request_data param #
        for request_data_object in request_data:
            if request_data_object == dict():
                continue

            # Validating request data object #
            try:
                validate_request_data_object(
                    declarative_meta, request_data_object
                )
            except Exception as e:
                # Appending error message #
                error_message_list.append(
                    build_object_error_message(
                        request_data_object, e
                    )
                )
                continue

            try:
                result = delete_object_by_full_match(
                    declarative_meta, request_data_object, main_connection_session
                )
            except Exception as e:
                error_message_list.append(
                    build_object_error_message(
                        request_data_object, str(e)
                    )
                )

                continue

            if result == 0:
                error_message_list.append(
                    build_object_error_message(
                        request_data_object, get_system_message(
                            'delete_no_items_found')
                    )
                )
                error_status_code = 404

        # Returning full success API built response #
        if error_message_list == get_system_empty_list():
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message(
                    'object_deleted_success')}
            )

        # Returning error list as an API built response #
        return build_proxy_response_insert_dumps_error_list(
            error_status_code, error_message_list
        )
    except Exception as e:
        return handle_custom_exception(e)


# Executes a stored procedure on the database #
def execute_sql_stored_procedure(stored_procedure_name, stored_procedure_args):
    try:
        # Connecting to the database and getting the engine
        main_connection_session = get_main_connection_session()
        engine = main_connection_session.bind
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    with engine.connect() as con:
        # Set OUT parameters as variables in the SQL session
        out_params = stored_procedure_args.get("out", {})
        for key, value in out_params.items():
            con.execute(text(f"SET @{key} = {value}"))

        in_values = ', '.join(
            [f"'{value}'" for value in stored_procedure_args.get("in", [])])
        call_proc = text(
            f"CALL {stored_procedure_name}({in_values}"
            f"{', ' if (out_params and in_values) else ''}"
            f"{', '.join([f'@{key}' for key in out_params])})"
        )

        try:
            stored_procedure_result = con.execute(call_proc)
            con.commit()
        except Exception as e:
            return handle_custom_exception(e)

        cursor = stored_procedure_result.cursor

        if out_params:
            # Fetch the OUT parameters
            fetched_out_params = {}
            for key in out_params:
                result = con.execute(text(f"SELECT @{key}"))
                fetched_out_params[key] = result.scalar()
            return build_proxy_response_insert_dumps(
                200, fetched_out_params
            )

        if cursor is not None:
            result = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(
                200, result
            )
        else:
            return build_proxy_response_insert_dumps(
                200, {get_system_message(
                    'message'): get_system_message('query_success')}
            )


# Method that retrieves a result list from database
def get_result_list(result, cursor):
    # Retrieving list of fields name #
    field_names = [i[0] for i in cursor.description]

    # Initializing result list #
    result_list = list()

    # Iterating over result #
    for result_object in result:
        # Creating new column dictionary #
        new_object = dict()
        # Iterating over field names #
        for i in range(len(field_names)):
            # Constructing column dict with field name #
            new_object[field_names[i]] = result_object[i]
        # Appending column dict in result list #
        result_list.append(new_object)
    # Returning result list #
    return result_list
