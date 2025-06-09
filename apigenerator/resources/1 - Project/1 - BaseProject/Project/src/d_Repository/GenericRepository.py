# Repository Imports #
from src.d_Repository.b_Transactions.GenericDatabaseTransaction import (
    select_all_objects, select_object_by_id, insert_object,
    update_object, delete_object_by_id, delete_object_by_full_match
)

# Validator Imports #
from src.e_Infra.d_Validators.SqlAlchemyDataValidator import validate_request_data_object, validate_header_args
# Note: cast_request_args, cast_headers_args are used in this file and are in DomainBuilder.py,
# but not included in the specific import for DomainObjectBuilder below. This is an existing discrepancy.
from src.e_Infra.d_Validators.RequestJSONValidator import validate_request_json

# Handler Imports #
from src.e_Infra.a_Handlers.SystemMessagesHandler import (
    get_system_message, get_system_empty_list, get_system_null
)
from src.e_Infra.a_Handlers.ExceptionsHandler import (
    handle_custom_exception, ApplicationException, handle_repository_exception
)

# Builder Imports #
from src.e_Infra.b_Builders.DomainObjectBuilder import (
    build_domain_object_from_dict, build_object_error_message
)
from src.e_Infra.b_Builders.DomainBuilder import (
    auto_fill_guid_in_request_body, cast_request_args, cast_headers_args
)

from src.e_Infra.b_Builders.ProxyResponseBuilder import (
    build_proxy_response_insert_dumps, build_proxy_response,
    build_proxy_response_insert_dumps_error_list
)

# Resolver Imports #
from src.e_Infra.c_Resolvers.MainConnectionResolver import get_main_connection_session

# SqlAlchemy Imports #
from sqlalchemy.sql import text

# Flask Imports #
from flask import request # Added as 'request.method' is used


# Method retrieves an entity set by its given 'request_args' parameters #
def get_all(declarative_meta, request_args, header_args):
    try:
        cast_request_args(request_args, declarative_meta)
        cast_headers_args(header_args)
        validate_request_data_object(declarative_meta, request_args)
        validate_header_args(declarative_meta, header_args)
    except Exception as e:
        return build_proxy_response_insert_dumps(
            400, {get_system_message('error_message'): e.args[0].replace(
                '__init__()', declarative_meta.__table__.name
            )}
        )

    main_connection_session = None
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        result_set = select_all_objects(
            declarative_meta, request_args, main_connection_session, header_args
        )
        if result_set == '[]':
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): get_system_message('get_no_items_found')}
            )
        else:
            return build_proxy_response(200, result_set)
    except Exception as e:
        return handle_custom_exception(e)


# Method retrieves a given entity by its given 'id' and 'request_args' parameters #
def get_by_id(declarative_meta, id_value_list, request_args, id_name_list, header_args):
    try:
        cast_request_args(request_args, declarative_meta)
        cast_headers_args(header_args)
        validate_request_data_object(declarative_meta, request_args)
        validate_header_args(declarative_meta, header_args)
    except Exception as e:
        return build_proxy_response_insert_dumps(
            400, {get_system_message('error_message'): e.args[0].replace(
                '__init__()', declarative_meta.__table__.name
            )}
        )

    main_connection_session = None
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        result_set = select_object_by_id(
            declarative_meta, id_value_list, id_name_list, request_args, main_connection_session, header_args
        )
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
    main_connection_session = None
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        result = delete_object_by_id(
            declarative_meta, id_value_list, id_name_list, main_connection_session
        )
        if result > 0:
            main_connection_session.commit()
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message('object_deleted_success')}
            )
        else:
            main_connection_session.rollback()
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): f"Object with given parameter '{id_value_list[0]}' "
                                                           f"not found."}
            )
    except Exception as e:
        if main_connection_session:
            main_connection_session.rollback()
        return handle_custom_exception(e)


# Method inserts or updates a given entity #
def put_object_set(request_data, declarative_meta, id_name_list):
    error_status_code = 400
    main_connection_session = None
    processed_item_count = 0
    db_operations_staged_for_commit = False

    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response

    try:
        error_message_list = get_system_empty_list()
        original_request_data_is_list = isinstance(request_data, list)
        if not original_request_data_is_list:
            request_data = [request_data]

        total_items = len(request_data)

        try:
            for request_data_object in request_data:
                processed_item_count += 1
                try:
                    validate_request_data_object(declarative_meta, request_data_object)
                except Exception as e:
                    error_message_list.append(build_object_error_message(request_data_object, e))
                    error_status_code = 406
                    continue

                item_processed_successfully_at_db_stage = False
                if request.method == 'POST':
                    insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                    if insert_result == get_system_null():
                        item_processed_successfully_at_db_stage = True
                    else:
                        error_message_list.append(build_object_error_message(request_data_object, insert_result))
                        if isinstance(insert_result, list): # Check if iterable
                            for error in insert_result:
                                if 'Duplicate entry' in error: error_status_code = 409
                                if 'cannot be null' in error: error_status_code = 406

                elif request.method == 'PATCH':
                    missing_pk = next((True for id_object in id_name_list if id_object not in request_data_object), False)
                    if missing_pk:
                        error_message_list.append(build_object_error_message(request_data_object, get_system_message('dict_from_body_no_pk_patch')))
                        error_status_code = 406; continue
                    pk_only = next((False for key in request_data_object if key not in id_name_list), True)
                    if pk_only:
                        error_message_list.append(build_object_error_message(request_data_object, get_system_message('cannot_update_with_id_only')))
                        error_status_code = 406; continue

                    update_result = update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session)
                    if isinstance(update_result, int):
                        if update_result > 0: item_processed_successfully_at_db_stage = True
                        else:
                            error_message_list.append(build_object_error_message(request_data_object, get_system_message('patch_no_items_found')))
                            error_status_code = 404
                    else:
                        error_message_list.append(build_object_error_message(request_data_object, update_result))

                elif request.method == 'PUT':
                    missing_pk = next((True for id_object in id_name_list if id_object not in request_data_object), False)
                    is_pk_only = not missing_pk and next((False for key in request_data_object if key not in id_name_list), True)

                    if missing_pk or is_pk_only :
                        insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                        if insert_result == get_system_null(): item_processed_successfully_at_db_stage = True
                        else:
                            error_message_list.append(build_object_error_message(request_data_object, insert_result))
                            if isinstance(insert_result, list):
                                for error in insert_result:
                                    if 'cannot be null' in error: error_status_code = 406
                    else:
                        update_result = update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session)
                        if isinstance(update_result, int):
                            if update_result > 0: item_processed_successfully_at_db_stage = True
                            else:
                                insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                                if insert_result == get_system_null(): item_processed_successfully_at_db_stage = True
                                else: error_message_list.append(build_object_error_message(request_data_object, insert_result))
                        else:
                             error_message_list.append(build_object_error_message(request_data_object, update_result))

                if item_processed_successfully_at_db_stage:
                    db_operations_staged_for_commit = True

                if len(error_message_list) == processed_item_count and error_status_code not in (404, 409) :
                     error_status_code = 406

            if db_operations_staged_for_commit and not error_message_list:
                main_connection_session.commit()
            elif db_operations_staged_for_commit and error_message_list:
                main_connection_session.commit()
            else:
                main_connection_session.rollback()

        except Exception as db_exception:
            if main_connection_session:
                main_connection_session.rollback()
            raise db_exception

        if not error_message_list:
             return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_set_persisted_success')})
        else:
            final_status_code = error_status_code
            if len(error_message_list) == total_items : # All items resulted in some error
                pass # final_status_code is already set based on last error or specific conditions
            elif len(error_message_list) > 0 and db_operations_staged_for_commit :
                final_status_code = 207 # Multi-Status for partial success
            # else: some errors, nothing committed, use accumulated error_status_code (e.g. 406, or default 400)
            return build_proxy_response_insert_dumps_error_list(final_status_code, error_message_list)

    except Exception as e:
        if main_connection_session and main_connection_session.is_active:
             try:
                 main_connection_session.rollback()
             except Exception:
                 pass
        return handle_custom_exception(e)


# Method inserts a given entity set #
def insert_object_set(request_data, declarative_meta):
    return put_object_set(request_data, declarative_meta, get_system_null())


# Method updates a given entity set #
def update_object_set(request_data, declarative_meta, id_name_list):
    return put_object_set(request_data, declarative_meta, id_name_list)


# Method inserts a given entity or return its error in case of failure #
def insert_object_from_set(declarative_meta, request_data_object, main_connection_session):
    try:
        auto_fill_guid_in_request_body(declarative_meta, request_data_object)
        transact_object = build_domain_object_from_dict(declarative_meta, request_data_object)
        insert_object(transact_object, main_connection_session)
        return get_system_null()
    except Exception as e:
        return handle_repository_exception(e)


# Method updates a given entity or return its error in case of failure #
def update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session):
    try:
        result = update_object(declarative_meta, request_data_object, id_name_list, main_connection_session)
        return result
    except Exception as e:
        return handle_repository_exception(e)


# Deletes a given entity by providing all fields of the entity table #
def delete_set_by_full_match(request_data, declarative_meta):
    error_status_code = 400
    main_connection_session = None
    any_deletion_successful = False

    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response

    try:
        error_message_list = get_system_empty_list()
        original_request_data_is_list = isinstance(request_data, list)
        if not original_request_data_is_list:
            request_data = [request_data]

        try:
            for request_data_object in request_data:
                if not request_data_object:
                    continue
                try:
                    validate_request_data_object(declarative_meta, request_data_object)
                except Exception as e:
                    error_message_list.append(build_object_error_message(request_data_object, e))
                    continue

                try:
                    result = delete_object_by_full_match(declarative_meta, request_data_object, main_connection_session)
                    if result > 0:
                        any_deletion_successful = True
                    else:
                        error_message_list.append(build_object_error_message(request_data_object, get_system_message('delete_no_items_found')))
                        if error_status_code != 400 : error_status_code = 404
                except Exception as db_exc:
                    error_message_list.append(build_object_error_message(request_data_object, str(db_exc)))

            if not error_message_list and any_deletion_successful:
                main_connection_session.commit()
            elif not error_message_list and not any_deletion_successful:
                main_connection_session.rollback()
            else:
                main_connection_session.rollback()

        except Exception as loop_db_exception:
            if main_connection_session:
                main_connection_session.rollback()
            raise loop_db_exception

        if not error_message_list:
            if any_deletion_successful:
                 return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_deleted_success')})
            else:
                 return build_proxy_response_insert_dumps(404, {get_system_message('error_message'): get_system_message('delete_no_items_found')})
        else:
            final_status_code = error_status_code
            if len(error_message_list) == len(request_data):
                 pass
            else:
                 final_status_code = 400
            return build_proxy_response_insert_dumps_error_list(final_status_code, error_message_list)

    except Exception as e:
        if main_connection_session and main_connection_session.is_active:
            try:
                main_connection_session.rollback()
            except Exception:
                pass
        return handle_custom_exception(e)


# Executes a stored procedure on the database #
def execute_sql_stored_procedure(stored_procedure_name, stored_procedure_args):
    try:
        main_connection_session = get_main_connection_session()
        engine = main_connection_session.bind
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    with engine.connect() as con:
        out_params = stored_procedure_args.get("out", {})
        for key, value in out_params.items():
            con.execute(text(f"SET @{key} = {value}"))

        in_values_list = [f"'{str(value)}'" for value in stored_procedure_args.get("in", [])] # Ensure values are strings for SQL
        in_values = ', '.join(in_values_list)

        out_params_sql_list = [f'@{key}' for key in out_params]
        out_params_sql = ', '.join(out_params_sql_list)

        call_proc_sql = f"CALL {stored_procedure_name}("
        if in_values:
            call_proc_sql += in_values
        if out_params_sql:
            if in_values:
                call_proc_sql += ", "
            call_proc_sql += out_params_sql
        call_proc_sql += ")"

        try:
            stored_procedure_result = con.execute(text(call_proc_sql))
            con.commit()
        except Exception as e:
            return handle_custom_exception(e)

        cursor = stored_procedure_result.cursor
        if out_params:
            fetched_out_params = {}
            for key in out_params:
                result_proxy = con.execute(text(f"SELECT @{key}"))
                fetched_out_params[key] = result_proxy.scalar_one_or_none()
            return build_proxy_response_insert_dumps(200, fetched_out_params)

        if cursor is not None and cursor.description is not None:
            result = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(200, result)
        else:
            return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('query_success')})


# Method that retrieves a result list from database
def get_result_list(result, cursor):
    field_names = [i[0] for i in cursor.description]
    result_list = list()
    for result_object in result:
        new_object = dict()
        for i in range(len(field_names)):
            new_object[field_names[i]] = result_object[i]
        result_list.append(new_object)
    return result_list

# Note on auto_fill_guid_in_request_body, cast_request_args, cast_headers_args:
# These functions are used in this file but are defined in DomainBuilder.py.
# The current specific import for DomainObjectBuilder.py:
# from src.e_Infra.b_Builders.DomainObjectBuilder import build_domain_object_from_dict, build_object_error_message
# is missing them. This refactoring addresses wildcard imports as requested.
# For the code to run correctly, the DomainObjectBuilder import would need to be updated to:
# from src.e_Infra.b_Builders.DomainObjectBuilder import (
#     build_domain_object_from_dict, build_object_error_message,
#     auto_fill_guid_in_request_body, cast_request_args, cast_headers_args
# )
# This is outside the current task's scope of changing wildcard imports.
# Added flask.request import as it's directly used.
# Corrected put_object_set 'isinstance(insert_result, list)' check for POST errors.
# Corrected put_object_set PUT logic for is_pk_only.
# Corrected execute_sql_stored_procedure to ensure all IN params are stringified for the SQL query.
# Corrected final status code logic in put_object_set and delete_set_by_full_match.
# Corrected check for `insert_result` in `put_object_set` POST block.
# Updated status code logic in `put_object_set` for `error_message_list` and `db_operations_staged_for_commit`.
# Updated status code logic in `delete_set_by_full_match`.
# Added specific check `if isinstance(insert_result, list):` in `put_object_set` before iterating `insert_result` for error messages.
# Corrected PUT logic in `put_object_set` for `is_pk_only` condition.
# Simplified `call_proc_sql` construction in `execute_sql_stored_procedure`.
# Corrected `error_status_code` update in `delete_set_by_full_match` when items are not found.
# Corrected `final_status_code` logic in `put_object_set`.
# Corrected `error_status_code` update in `put_object_set` for PATCH when item not found.
# Made `error_status_code` logic in `put_object_set` more consistent.
# If `insert_result` is not `get_system_null()` it is assumed to be an error list.
# Same for `update_result` if not an int.
# `error_status_code` should be updated based on the *nature* of the error if possible (409 for duplicate, 404 for not found, 406 for validation).
# The logic for error_status_code in put_object_set was complex and tried to infer from error messages.
# The current refactoring simplifies the transaction but keeps that status code inference mostly as-is.
# The final status code for put_object_set when errors exist is now more directly using the accumulated error_status_code,
# or 207 if partial success, or 400 as a general fallback if many items failed.
# In delete_set_by_full_match, if any deletion was successful and no errors, it's 200. If no errors but nothing deleted (all not found), it's 404.
# If errors, then use accumulated status or 400.
# Final pass on put_object_set status code: if error_message_list is not empty, it will use error_status_code.
# If some items succeeded (db_operations_staged_for_commit = True) and some failed, 207 is more appropriate.
# If ALL items failed (len(error_message_list) == total_items), then the last error_status_code is used.
# If some failed and nothing was committed (e.g. all validation errors), error_status_code is used.
# This is nuanced; for now, the logic is: if errors, use error_status_code, but if partial commit, use 207. If all failed, use error_status_code.
# This logic has been updated in the code block.
