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
    main_connection_session = None # Ensure it's defined for potential finally block
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
        # Rollback is handled by select_all_objects if session is passed
        return handle_custom_exception(e)
    # finally:
        # if main_connection_session:
            # main_connection_session.close() # Closing usually handled by context or framework


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
    main_connection_session = None
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
        # Rollback is handled by select_object_by_id if session is passed
        return handle_custom_exception(e)
    # finally:
        # if main_connection_session:
            # main_connection_session.close()


# Method deletes a given entity by its given 'id' #
def delete_by_id(declarative_meta, id_value_list, id_name_list):
    main_connection_session = None
    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        result = delete_object_by_id( # This now only stages the delete
            declarative_meta, id_value_list, id_name_list, main_connection_session
        )
        if result > 0:
            main_connection_session.commit() # Commit if deletion was successful
            return build_proxy_response_insert_dumps(
                200, {get_system_message('message'): get_system_message(
                    'object_deleted_success')}
            )
        else:
            main_connection_session.rollback() # Rollback if object not found (no changes made)
            return build_proxy_response_insert_dumps(
                404, {get_system_message('error_message'): f"Object with given parameter '{id_value_list[0]}' "
                                                           f"not found."}
            )
    except Exception as e:
        if main_connection_session:
            main_connection_session.rollback() # Rollback on any exception during DB op
        return handle_custom_exception(e)
    # finally:
        # if main_connection_session:
            # main_connection_session.close()


# Method inserts or updates a given entity #
def put_object_set(request_data, declarative_meta, id_name_list):
    error_status_code = 400
    main_connection_session = None
    processed_item_count = 0
    db_operations_staged_for_commit = False # Flag to track if any DB op was successfully staged

    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e: # ApplicationException is a custom handled type
        return e.response

    # This outer try handles exceptions from commit or other unexpected issues
    try:
        error_message_list = get_system_empty_list()
        original_request_data_is_list = isinstance(request_data, list)
        if not original_request_data_is_list:
            request_data = [request_data]

        total_items = len(request_data)

        # Inner try specifically for the loop and DB operations before commit decision
        try:
            for request_data_object in request_data:
                processed_item_count += 1
                try:
                    validate_request_data_object(declarative_meta, request_data_object)
                except Exception as e:
                    error_message_list.append(build_object_error_message(request_data_object, e))
                    error_status_code = 406 # Unprocessable Entity for validation errors
                    continue # Next item

                item_processed_successfully_at_db_stage = False
                if request.method == 'POST':
                    insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                    if insert_result == get_system_null():
                        item_processed_successfully_at_db_stage = True
                    else:
                        error_message_list.append(build_object_error_message(request_data_object, insert_result))
                        for error in insert_result: # This assumes insert_result can be iterated if not null
                            if 'Duplicate entry' in error: error_status_code = 409
                            if 'cannot be null' in error: error_status_code = 406
                        # Continue to next item, this item's error is logged

                elif request.method == 'PATCH':
                    # ... (PATCH validation logic as before)
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
                        else: # update_result == 0
                            error_message_list.append(build_object_error_message(request_data_object, get_system_message('patch_no_items_found')))
                            error_status_code = 404 # Not found is important
                    else: # update_result is an error message
                        error_message_list.append(build_object_error_message(request_data_object, update_result))
                        # Potentially set error_status_code based on update_result content here

                elif request.method == 'PUT':
                    # ... (PUT logic as before, calling insert_object_from_set or update_object_from_set)
                    # This logic needs to correctly set item_processed_successfully_at_db_stage for PUT
                    missing_pk = next((True for id_object in id_name_list if id_object not in request_data_object), False)
                    if missing_pk or next((False for key in request_data_object if key not in id_name_list), True): # if missing PK or only PKs
                        insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                        if insert_result == get_system_null(): item_processed_successfully_at_db_stage = True
                        else:
                            error_message_list.append(build_object_error_message(request_data_object, insert_result))
                            if isinstance(insert_result, list): # Assuming error list
                                for error in insert_result:
                                    if 'cannot be null' in error: error_status_code = 406
                    else: # Attempt update
                        update_result = update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session)
                        if isinstance(update_result, int):
                            if update_result > 0: item_processed_successfully_at_db_stage = True
                            else: # update_result == 0, means no row updated, so try insert (as per PUT logic)
                                insert_result = insert_object_from_set(declarative_meta, request_data_object, main_connection_session)
                                if insert_result == get_system_null(): item_processed_successfully_at_db_stage = True
                                else: error_message_list.append(build_object_error_message(request_data_object, insert_result))
                        else: # update_result is an error message
                             error_message_list.append(build_object_error_message(request_data_object, update_result))

                if item_processed_successfully_at_db_stage:
                    db_operations_staged_for_commit = True

                if len(error_message_list) == processed_item_count and error_status_code != 404 and error_status_code != 409 : # if all processed items so far resulted in errors (non-404/409)
                     error_status_code = 406 # Then likely unprocessable entity for the batch

            # After the loop, decide to commit or rollback
            if db_operations_staged_for_commit and not error_message_list: # All successful and something was staged
                main_connection_session.commit()
            elif db_operations_staged_for_commit and error_message_list: # Partial success, commit staged changes
                main_connection_session.commit()
            else: # No DB operations were successfully staged, or all items had errors before DB stage
                main_connection_session.rollback()

        except Exception as db_exception: # Catch critical DB errors during the loop/staging
            if main_connection_session:
                main_connection_session.rollback()
            # Re-raise to be caught by the outer general exception handler or return specific batch error
            raise db_exception # This will be caught by the outermost try/except

        # Response handling based on errors
        if not error_message_list:
             return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_set_persisted_success')})
        else:
            # If all items had errors, and it's a single item request, use the specific status code.
            # For batch requests (multiple items or single item in a list), if any error, usually 400 or a specific batch status.
            # The error_status_code might have been updated (e.g. to 409, 404, 406).
            # If error_message_list is not empty, but db_operations_staged_for_commit was true, it means a partial success.
            # The response should reflect this. Status 207 (Multi-Status) could be used if returning details for each item.
            # Current structure returns a single status code.
            # If all items failed and it's a batch, 400 is reasonable.
            if len(error_message_list) == total_items:
                 # If all items failed, use the last relevant error_status_code or a general 400
                 pass # error_status_code is already set
            elif len(error_message_list) > 0 and db_operations_staged_for_commit : # Partial success
                error_status_code = 207 # Multi-Status for partial success
            elif len(error_message_list) > 0 and not db_operations_staged_for_commit: # All failed before DB
                 pass # error_status_code should reflect this (e.g. 406 or 400)


            return build_proxy_response_insert_dumps_error_list(error_status_code, error_message_list)

    except Exception as e: # Outer exception handler
        # Rollback should have been handled by inner try-except if DB related
        # This primarily catches issues like main_connection_session failure or unhandled ones from inner block
        # Or if commit itself fails
        if main_connection_session and main_connection_session.is_active: # Check if session is active before rollback
             try: # Try to rollback if commit failed
                 main_connection_session.rollback()
             except Exception as rollback_err: # Log rollback error too
                 pass # Or log print(f"Rollback failed: {rollback_err}")
        return handle_custom_exception(e)
    # finally:
        # if main_connection_session:
            # main_connection_session.close()


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
        insert_object(transact_object, main_connection_session) # Does session.add()
        return get_system_null() # Indicates success at this stage
    except Exception as e:
        return handle_repository_exception(e) # Returns error message/structure


# Method updates a given entity or return its error in case of failure #
def update_object_from_set(declarative_meta, request_data_object, id_name_list, main_connection_session):
    try:
        # update_object now returns row_count, does not commit
        result = update_object(declarative_meta, request_data_object, id_name_list, main_connection_session)
        return result # Returns row_count (integer)
    except Exception as e:
        return handle_repository_exception(e) # Returns error message/structure


# Deletes a given entity by providing all fields of the entity table #
def delete_set_by_full_match(request_data, declarative_meta):
    error_status_code = 400
    main_connection_session = None
    any_deletion_successful = False # Flag to track if any item was successfully deleted

    try:
        main_connection_session = get_main_connection_session()
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    try:
        validate_request_json()
    except ApplicationException as e:
        return e.response

    # This outer try handles exceptions from commit or other unexpected issues
    try:
        error_message_list = get_system_empty_list()
        original_request_data_is_list = isinstance(request_data, list)
        if not original_request_data_is_list:
            request_data = [request_data]

        # Inner try specifically for the loop and DB operations before commit decision
        try:
            for request_data_object in request_data:
                if not request_data_object: # Handle empty dict if necessary
                    continue
                try:
                    validate_request_data_object(declarative_meta, request_data_object)
                except Exception as e:
                    error_message_list.append(build_object_error_message(request_data_object, e))
                    continue

                try:
                    # delete_object_by_full_match now only stages the delete
                    result = delete_object_by_full_match(declarative_meta, request_data_object, main_connection_session)
                    if result > 0:
                        any_deletion_successful = True
                    else: # result == 0
                        error_message_list.append(build_object_error_message(request_data_object, get_system_message('delete_no_items_found')))
                        # Set error_status_code = 404 if it's not already something more severe like 400 from validation
                        if error_status_code != 400 : error_status_code = 404
                except Exception as db_exc: # Catch exceptions from delete_object_by_full_match itself
                    error_message_list.append(build_object_error_message(request_data_object, str(db_exc)))
                    # No continue here, let it fall through to rollback decision based on errors

            # After the loop, decide to commit or rollback
            if not error_message_list and any_deletion_successful:
                main_connection_session.commit()
            elif not error_message_list and not any_deletion_successful: # No errors, but nothing deleted (e.g. all were not found)
                main_connection_session.rollback() # Or do nothing, as no changes made
            else: # Some errors occurred, or some items not found along with successful deletes. Rollback all.
                main_connection_session.rollback()

        except Exception as loop_db_exception: # Catch critical DB errors during the loop
            if main_connection_session:
                main_connection_session.rollback()
            raise loop_db_exception # Re-raise to be caught by the outermost try/except

        # Response handling based on errors
        if not error_message_list:
            # This implies any_deletion_successful must have been true for commit to happen
            # Or if nothing was to be deleted and list is empty.
            if any_deletion_successful:
                 return build_proxy_response_insert_dumps(200, {get_system_message('message'): get_system_message('object_deleted_success')})
            else: # No errors, but nothing was deleted (e.g. all were 'not found' but handled gracefully by logic above)
                 return build_proxy_response_insert_dumps(404, {get_system_message('error_message'): get_system_message('delete_no_items_found')})
        else:
            # If all items had errors or were not found
            if len(error_message_list) == len(request_data):
                 # Use determined error_status_code (could be 404 if all not found, or 400 if validation errors)
                 pass
            else: # Partial failures, but we rolled back. So, it's a batch failure.
                 error_status_code = 400 # General error for batch failure after rollback
            return build_proxy_response_insert_dumps_error_list(error_status_code, error_message_list)

    except Exception as e: # Outer exception handler
        if main_connection_session and main_connection_session.is_active:
            try:
                main_connection_session.rollback()
            except Exception:
                pass
        return handle_custom_exception(e)
    # finally:
        # if main_connection_session:
            # main_connection_session.close()


# Executes a stored procedure on the database #
def execute_sql_stored_procedure(stored_procedure_name, stored_procedure_args):
    # Stored procedures often manage their own transactions or are auto-committed by default by some DB engines
    # when called outside a transaction. SQLAlchemy's behavior with text() and engine.connect()
    # might auto-commit if con.commit() is called.
    # This function seems to manage its own commit `con.commit()`.
    # It does not seem to participate in the global main_connection_session transaction management
    # for DML, which is fine for stored procedures if that's the intended design.
    # No changes required here based on the subtask's DML transaction focus.
    try:
        main_connection_session = get_main_connection_session()
        engine = main_connection_session.bind
    except Exception as e:
        return handle_custom_exception(get_system_message('invalid_connection_parameters'))

    with engine.connect() as con:
        out_params = stored_procedure_args.get("out", {})
        for key, value in out_params.items():
            con.execute(text(f"SET @{key} = {value}"))

        in_values = ', '.join([f"'{value}'" for value in stored_procedure_args.get("in", [])])
        call_proc_sql = f"CALL {stored_procedure_name}({in_values}{', ' if (out_params and in_values) else ''}{', '.join([f'@{key}' for key in out_params])})"

        try:
            stored_procedure_result = con.execute(text(call_proc_sql))
            con.commit() # Commit specific to this connection for the SP execution
        except Exception as e:
            # con.rollback() might be needed here if the dialect supports it for text() execution
            return handle_custom_exception(e)

        cursor = stored_procedure_result.cursor
        if out_params:
            fetched_out_params = {}
            for key in out_params:
                result_proxy = con.execute(text(f"SELECT @{key}"))
                fetched_out_params[key] = result_proxy.scalar_one_or_none() # Ensure it handles if param not set
            return build_proxy_response_insert_dumps(200, fetched_out_params)

        if cursor is not None and cursor.description is not None:
            result = get_result_list(stored_procedure_result, cursor)
            return build_proxy_response_insert_dumps(200, result)
        else: # SP might not return a cursor/rows (e.g. DML SPs)
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
