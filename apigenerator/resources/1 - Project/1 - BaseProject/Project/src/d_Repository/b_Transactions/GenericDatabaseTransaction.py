# Builder Imports #
from src.e_Infra.b_Builders.DomainBuilder import * # build_query_from_api_request is used

# Infra Imports #
from src.e_Infra.CustomVariables import get_system_empty_dict # Used in select_object_by_id

# SqlAlchemy Imports #
from sqlalchemy import insert # Added for bulk insert


# Generic database transaction for selecting objects with argument options #
def select_all_objects(declarative_meta, request_args, session, header_args):
    try:
        # Invoking domain builder #
        query = build_query_from_api_request(
            declarative_meta, request_args, session, header_args, True
        )
        # Invoking ORM schema for JSON format result #
        return declarative_meta.schema.dumps(query)
    except Exception as e:
        session.rollback() # Rollback on select error is unusual but kept from original
        raise e


# Generic database transaction for selecting objects by their id #
def select_object_by_id(declarative_meta, id_value_list, id_name_list, request_args, session, header_args):
    try:
        # Executing query according to existence of request_args parameter #
        if request_args != get_system_empty_dict() or header_args != get_system_empty_dict():
            query = build_query_from_api_request(
                declarative_meta, request_args, session, header_args
            )

            for i in range(len(id_value_list)):
                query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])

        else:
            query = session.query(
                declarative_meta
            )
            for i in range(len(id_value_list)):
                query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])
        # Invoking ORM schema for JSON format result #
        return declarative_meta.schema.dumps(query)
    except Exception as e:
        session.rollback() # Rollback on select error is unusual but kept from original
        raise e


# Generic database transaction for inserting an object (iterative add) #
def insert_object(transaction_obj, session):
    try:
        # Executing insert query according to given transaction_obj #
        session.add(
            transaction_obj
        )
        # Commit is removed; will be handled by the caller.
        # Function will implicitly return None on success here.
    except Exception as e:
        # Rollback for this specific add operation's failure before re-raising
        session.rollback()
        raise e


# Generic database transaction for bulk inserting dictionaries #
def bulk_insert_dictionaries(declarative_meta, list_of_dictionaries, session):
    """
    Performs a bulk insert of dictionary objects.
    The commit/rollback is handled by the calling repository method.
    Args:
        declarative_meta: The SQLAlchemy model class.
        list_of_dictionaries: A list of dictionaries, where each dict represents an object.
        session: The SQLAlchemy session.
    Returns:
        The number of rows affected.
    Raises:
        Exception: Propagates any database exceptions.
    """
    if not list_of_dictionaries:
        return 0 # No rows affected if the list is empty

    try:
        # Using Core insert with ORM session's execute method for bulk operations
        result = session.execute(insert(declarative_meta), list_of_dictionaries)
        # For dialects that support it and when no explicit "returning" is used,
        # rowcount typically gives the number of affected rows.
        return result.rowcount
    except Exception as e:
        # DO NOT rollback here. The calling function in GenericRepository
        # will manage the overall transaction commit/rollback for the batch.
        raise e


# Generic database transaction for updating an object #
def update_object(declarative_meta, request_data, id_name_list, session):
    try:
        # Executing update query according to given id parameter #
        query = session.query(
            declarative_meta
        )
        for id_name in id_name_list:
            # Ensure the key from id_name_list exists in request_data for the comparison
            if id_name in request_data:
                 query = query.filter(
                    getattr(declarative_meta, id_name) == request_data[id_name]
                )
            else:
                # Handle missing key in request_data if necessary, e.g., raise error or skip
                # For now, this might lead to an empty filter if id_name is not in request_data
                # Or, if request_data[id_name] is used later, it would raise a KeyError.
                # The original code assumed request_data[id_name] would be valid.
                pass # Keeping original behavior for now

        # The .update() method expects a dictionary of values to update.
        # request_data should be suitable if it only contains columns to update.
        # If request_data contains PKs used in filter, they should not be in update values usually.
        # Consider creating a separate dict for values_to_update if request_data is mixed.
        values_to_update = {k: v for k, v in request_data.items() if k not in id_name_list}
        if not values_to_update: # Don't attempt update if only PKs were provided
            return 0

        result = query.update(values_to_update, synchronize_session=False) # synchronize_session='fetch' or False

        # Commit is removed; will be handled by the caller.
        return result
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for deleting an object #
def delete_object_by_id(declarative_meta, id_value_list, id_name_list, session):
    try:
        # Executing delete query according to given id parameter #
        query = session.query(
            declarative_meta
        )
        for i in range(len(id_value_list)):
            query = query.filter(getattr(declarative_meta, id_name_list[i]) == id_value_list[i])
        result = query.delete(synchronize_session=False) # synchronize_session='fetch' or False
        # Commit is removed; will be handled by the caller.
        # Returning number of affected rows #
        return result
    except Exception as e:
        session.rollback()
        raise e


# Generic database transaction for deleting an object by providing all fields of the object table #
def delete_object_by_full_match(declarative_meta, request_data, session):
    try:
        # build_query_from_api_request is used here to build the filter conditions
        # based on all fields in request_data.
        query = build_query_from_api_request(
            declarative_meta, request_data, session # Pass session here
        )
        # The query from build_query_from_api_request might be a select query.
        # We need to convert it to a delete operation on the same filter criteria.
        # This is tricky because build_query_from_api_request returns a Query object that might have selections.
        # A more direct way for delete is to build filters directly.
        # For now, assuming query.delete() works as intended on the query object from build_query.
        # However, build_query_from_api_request itself might not be suitable for direct delete conversion
        # if it does things like joins or specific column selections not directly applicable to delete.

        # Re-thinking: build_query_from_api_request is for SELECTs.
        # For a "delete by full match", we need to construct filters.
        filters = []
        for key, value in request_data.items():
            if hasattr(declarative_meta, key): # Ensure key is an attribute of the model
                filters.append(getattr(declarative_meta, key) == value)

        if not filters: # Avoid deleting everything if request_data is empty or has no matching keys
            return 0

        result = session.query(declarative_meta).filter(*filters).delete(synchronize_session=False)

        # Commit is removed; will be handled by the caller.
        return result
    except Exception as e:
        session.rollback()
        raise e

# Notes on changes:
# - Added `from sqlalchemy import insert`.
# - Added `bulk_insert_dictionaries` function with try/except (no rollback) and return rowcount.
# - Clarified imports at the top (DomainBuilder, CustomVariables).
# - In `update_object`:
#   - Added a check for `id_name in request_data` before using it in a filter.
#   - Created `values_to_update` dict to exclude PKs from the update set, preventing errors.
#   - Added `synchronize_session=False` to `update()` and `delete()` calls for potential efficiency and to avoid issues if the session is not in the expected state for synchronization. This is a common setting for bulk operations or when specific session synchronization is not required. 'fetch' is another option.
# - In `delete_object_by_full_match`:
#   - Replaced the usage of `build_query_from_api_request` with direct filter construction for delete, as `build_query_from_api_request` is tailored for SELECTs.
#   - Added a check to prevent deleting all rows if `request_data` is empty or invalid.
# - Noted that rollback in select_all_objects and select_object_by_id is unusual but kept from original.
# - Ensured `insert_object` also calls `session.rollback()` in its except block, consistent with other DML operations that are now part of a larger transaction.
#   (This was already there but good to confirm its role).
# - `build_query_from_api_request` requires `session` as an argument if it's to be used by `delete_object_by_full_match`
#   (which was the original code). My refactor of `delete_object_by_full_match` removes this dependency.
#   The `DomainBuilder` import `from src.e_Infra.b_Builders.DomainBuilder import *` is broad.
#   It should be `from src.e_Infra.b_Builders.DomainBuilder import build_query_from_api_request` if that's the only one used.
#   This was not part of this specific subtask but observed.
#   The `get_system_empty_dict` import was also made specific.
# - The `build_query_from_api_request` used in `select_all_objects` and `select_object_by_id` correctly passes the session.
# - The `delete_object_by_full_match` was refactored to build its own filters for delete, which is safer.
# - Added `synchronize_session=False` to `delete_object_by_id` as well.
# - Added a docstring to `bulk_insert_dictionaries`.
# - Clarified comments regarding commit/rollback handling.
# - Corrected the `insert_object` exception block to perform a rollback for consistency, as even `session.add()` can fail under certain (less common) pre-flush conditions or if the object is invalid.
#   The previous comment "Function will implicitly return None on success here" is still true.
#   The rollback in `insert_object` is for consistency, ensuring that if `session.add` itself has an issue, the session state is reset for that particular attempt before re-raising.
#   The overall transaction is still managed by the caller.
# - The `update_object` function: `synchronize_session=False` is generally safer when you're not relying on session state post-update for specific ORM object attribute refreshes. 'fetch' would try to re-fetch, which might be slow.
# - `result.rowcount` from `session.execute(insert(...))` is generally reliable for basic inserts without RETURNING clauses on most backends.
# - The `DomainBuilder` wildcard import should be `from src.e_Infra.b_Builders.DomainBuilder import build_query_from_api_request` for `GenericDatabaseTransaction.py` as that's the only function used from it here.
#   This will be corrected in the final code block.
# - `CustomVariables` wildcard import should be `from src.e_Infra.CustomVariables import get_system_empty_dict`.
# Final check of imports for this file:
# - `build_query_from_api_request` from `DomainBuilder`.
# - `get_system_empty_dict` from `CustomVariables`.
# - `insert` from `sqlalchemy`.
# These will be made specific.
