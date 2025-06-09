# Repository Imports #
from src.d_Repository.b_Transactions.GenericDatabaseTransaction import (
    select_all_objects, select_object_by_id, insert_object,
    update_object, delete_object_by_id, delete_object_by_full_match,
    bulk_insert_dictionaries # Added for bulk insert strategy
)

# Validator Imports #
from src.e_Infra.d_Validators.SqlAlchemyDataValidator import validate_request_data_object, validate_header_args
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

# Variables Imports #
from src.e_Infra.GlobalVariablesManager import get_global_variable # Added for batch strategy

# SqlAlchemy Imports #
from sqlalchemy.sql import text

# Flask Imports #
from flask import request


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
    db_operations_staged_for_commit = False

    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response

    try: # This outer try handles commit exceptions or re-raised db_exceptions
        error_message_list = get_system_empty_list()
        original_request_data_is_list = isinstance(request_data, list)
        if not original_request_data_is_list:
            request_data = [request_data]

        total_items = len(request_data)
        processed_item_count = 0 # Moved inside outer try

        # Inner try specifically for the loop and DB operations before commit decision
        try:
            if request.method == 'POST':
                batch_strategy = get_global_variable('API_BATCH_INSERT_STRATEGY')
                if batch_strategy == 'BULK':
                    valid_dictionaries_for_bulk_insert = []
                    for request_data_object in request_data:
                        processed_item_count += 1
                        try:
                            validate_request_data_object(declarative_meta, request_data_object)
                            auto_fill_guid_in_request_body(declarative_meta, request_data_object) # Prepare dict for bulk
                            valid_dictionaries_for_bulk_insert.append(request_data_object)
                        except Exception as e:
                            error_message_list.append(build_object_error_message(request_data_object, e))
                            error_status_code = 406
                            # Continue to validate other items for error reporting

                    if valid_dictionaries_for_bulk_insert:
                        if len(valid_dictionaries_for_bulk_insert) == total_items: # All items are valid
                            # Attempt bulk insert only if all items validated successfully for 'BULK' strategy
                            # because bulk errors are typically all-or-nothing and hard to map back to individual items.
                            bulk_insert_dictionaries(declarative_meta, valid_dictionaries_for_bulk_insert, main_connection_session)
                            db_operations_staged_for_commit = True
                        else:
                            # If some items failed validation, do not proceed with bulk insert for the valid ones.
                            # Add a general error indicating partial validation failure for bulk mode.
                            # This makes 'BULK' more all-or-nothing even at validation stage.
                            # Alternatively, could insert the valid ones and report errors for others, but that's more 'ITERATIVE'.
                            # For now, if any validation fails in BULK mode, consider the whole batch problematic for insertion.
                            # The individual validation errors are already in error_message_list.
                             error_status_code = 406 # Unprocessable due to validation errors in some items
                             # No db_operations_staged_for_commit = True
                else: # ITERATIVE (or default) strategy for POST
                    for request_data_object in request_data:
                        processed_item_count += 1
                        try:
                            validate_request_data_object(declarative_meta, request_data_object)
                        except Exception as e:
                            error_message_list.append(build_object_error_message(request_data_object, e))
                            error_status_code = 406; continue

                        insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                        if insert_result == get_system_null():
                            db_operations_staged_for_commit = True
                        else:
                            error_message_list.append(build_object_error_message(request_data_object, insert_result))
                            if isinstance(insert_result, list):
                                for error in insert_result:
                                    if 'Duplicate entry' in error: error_status_code = 409
                                    elif 'cannot be null' in error: error_status_code = 406

            elif request.method in ['PATCH', 'PUT']: # Common loop for PATCH and PUT item processing
                for request_data_object in request_data:
                    processed_item_count += 1
                    try:
                        validate_request_data_object(declarative_meta, request_data_object)
                    except Exception as e:
                        error_message_list.append(build_object_error_message(request_data_object, e))
                        error_status_code = 406; continue

                    item_processed_successfully_at_db_stage = False
                    if request.method == 'PATCH':
                        missing_pk = next((True for id_obj in id_name_list if id_obj not in request_data_object), False)
                        if missing_pk:
                            error_message_list.append(build_object_error_message(request_data_object, get_system_message('dict_from_body_no_pk_patch')))
                            error_status_code = 406; continue
                        pk_only = next((False for k in request_data_object if k not in id_name_list), True)
                        if pk_only:
                            error_message_list.append(build_object_error_message(request_data_object, get_system_message('cannot_update_with_id_only')))
                            error_status_code = 406; continue

                        update_result = update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session)
                        if isinstance(update_result, int):
                            if update_result > 0: item_processed_successfully_at_db_stage = True
                            else:
                                error_message_list.append(build_object_error_message(request_data_object, get_system_message('patch_no_items_found')))
                                if error_status_code != 406: error_status_code = 404 # Prioritize 406 if already set
                        else:
                            error_message_list.append(build_object_error_message(request_data_object, update_result))

                    elif request.method == 'PUT':
                        missing_pk = next((True for id_obj in id_name_list if id_obj not in request_data_object), False)
                        is_pk_only = not missing_pk and next((False for k in request_data_object if k not in id_name_list), True)

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

            # After the loop, decide to commit or rollback
            if db_operations_staged_for_commit: # If any operation was successfully staged
                if not error_message_list: # All items processed successfully
                    main_connection_session.commit()
                else: # Some items had errors, but others were staged
                    # This is a partial success scenario. Commit the successful ones.
                    main_connection_session.commit()
            else: # No DB operations were successfully staged (e.g., all items had validation errors, or BULK validation failed)
                main_connection_session.rollback()

        except Exception as db_exception: # Catch critical DB errors during the loop/staging (e.g. from bulk_insert)
            if main_connection_session:
                main_connection_session.rollback()
            raise db_exception # Re-raise to be caught by the outermost try/except

        # Response handling based on errors
        if not error_message_list:
             return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_set_persisted_success')})
        else:
            final_status_code = error_status_code # Use accumulated status_code
            # If all items had errors (no successful staging)
            if len(error_message_list) == total_items and not db_operations_staged_for_commit:
                pass # final_status_code is already set
            # If some items had errors, but other operations were committed (partial success)
            elif len(error_message_list) > 0 and db_operations_staged_for_commit:
                final_status_code = 207 # Multi-Status for partial success
            # If all items had some form of error and nothing was committed.
            # (This might overlap with the first condition, but ensures a fallback)
            elif len(error_message_list) == total_items:
                pass # error_status_code should reflect the most relevant error (e.g. 406, 409, 404)

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
    # This function now implicitly uses the strategy defined by API_BATCH_INSERT_STRATEGY via put_object_set
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
                    error_status_code = 406 # Default to 406 for validation errors
                    continue

                try:
                    result = delete_object_by_full_match(declarative_meta, request_data_object, main_connection_session)
                    if result > 0:
                        any_deletion_successful = True
                    else:
                        error_message_list.append(build_object_error_message(request_data_object, get_system_message('delete_no_items_found')))
                        if error_status_code != 406: error_status_code = 404 # Prioritize 406
                except Exception as db_exc:
                    error_message_list.append(build_object_error_message(request_data_object, str(db_exc)))
                    error_status_code = 500 # DB error during delete

            if not error_message_list and any_deletion_successful:
                main_connection_session.commit()
            elif not error_message_list and not any_deletion_successful:
                main_connection_session.rollback()
            else: # Some errors occurred
                main_connection_session.rollback()

        except Exception as loop_db_exception:
            if main_connection_session:
                main_connection_session.rollback()
            raise loop_db_exception

        if not error_message_list:
            if any_deletion_successful:
                 return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_deleted_success')})
            else: # No errors, but nothing deleted (e.g. all were 'not found' but handled by rollback)
                 return build_proxy_response_insert_dumps(404, {get_system_message('error_message'): get_system_message('delete_no_items_found')})
        else: # Errors occurred
            final_status_code = error_status_code # Use accumulated error status
            # If all items in batch had an error
            if len(error_message_list) == len(request_data):
                pass # error_status_code should reflect the dominant error (e.g. 404 if all not found, 406 if all validation, 500 if a DB error happened)
            else: # Partial errors, but we rolled back the entire batch.
                 final_status_code = 400 # General error for batch failure after rollback if not all items had errors.
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

        in_values_list = [f"'{str(value)}'" for value in stored_procedure_args.get("in", [])]
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
            result_data = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(200, result_data)
        else:
            return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('query_success')})


# Method that retrieves a result list from database
def get_result_list(result, cursor):
    field_names = [i[0] for i in cursor.description]
    return [dict(zip(field_names, row)) for row in result]
