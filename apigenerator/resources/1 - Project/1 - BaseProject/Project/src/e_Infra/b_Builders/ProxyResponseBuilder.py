# System Imports #
import json
import re

# Infra Imports #
from src.e_Infra.CustomVariables import *

# Flask Imports #
from flask import Response

# Pre-compiled regex for extract_pymysql_error_log
PYMYSQL_ERROR_START_PATTERN = re.compile(r"\(pymysql\.err\.\w+\) \(\d+, ['\"]")

# Method builds a response with json.dumps and adding error list attribute #
def build_proxy_response_insert_dumps_error_list(status_code, error_message_list):
    # Building error final list structure #
    error_list = get_system_empty_dict()
    if error_message_list != get_system_empty_list():
        error_list['error_list'] = error_message_list
    # Returning error list as an API built response #
    return build_proxy_response_insert_dumps(status_code, error_list)


# Method builds a clean json response.
# Assumes 'body' is an already JSON-encoded string.
def build_proxy_response(status_code, body):
    log_body_content = body # Default to body as string if parsing fails
    try:
        # Attempt to parse the JSON string body for structured logging
        log_body_content = json.loads(body)
    except (json.JSONDecodeError, TypeError):
        # If body is not a valid JSON string or not a string type,
        # log_body_content remains the original body.
        # This might happen if body is None or an unexpected type.
        pass # log_body_content is already set to body

    try:
        log_payload = {"statusCode": status_code, "body": log_body_content}
        print_logs(json.dumps(log_payload, default=str))
    except Exception:
        # Fallback if logging the structured payload fails for any reason
        # For example, if log_body_content was an unhandled complex object.
        print_logs(json.dumps({"statusCode": status_code, "body": "Error during log serialization"}, default=str))

    return Response(response=body, status=status_code, content_type='application/json')


# Method builds a response with json.dumps #
# Assumes 'body' is a Python object (dict/list) to be serialized.
def build_proxy_response_insert_dumps(status_code, body):
    try:
        # For logging, body is used directly as it's a Python object here.
        log_payload = {"statusCode": status_code, "body": body}
        print_logs(json.dumps(log_payload, default=str))
    except Exception:
        print_logs(json.dumps({"statusCode": status_code, "body": "Error during log serialization"}, default=str))

    return Response(response=json.dumps(body, sort_keys=True, default=str), status=status_code, content_type='application/json')


def build_dto_error_message(e):
    response = str(e).replace("'<class ", "").replace(">')", "")\
        .replace(">'", "").replace('__init__()', 'JSON body').replace("Parameter validation failed:", "")\
        .replace('typing.', '').replace('Expecting value: line 1 column 1 (char 0)', 'JSON body empty').strip()
    return response


def build_sql_error_table_does_not_exist(original_exception):
    table_does_not_exist_error_list = ["Table", "doesn't exist"]
    if all(x in original_exception for x in table_does_not_exist_error_list):
        return True
    else:
        return False


def build_sql_error_invalid_syntax(original_exception):
    invalid_syntax_error_list = ["You have an error in your SQL syntax"]
    if all(x in original_exception for x in invalid_syntax_error_list):
        return True
    else:
        return False


def build_sql_error_duplicate_entry(original_exception):
    table_duplicate_entry_error_list = ["Duplicate entry", "for key"]
    if all(x in original_exception for x in table_duplicate_entry_error_list):
        return extract_pymysql_error_log(original_exception)
    else:
        return None


def build_sql_error_missing_foreign_key(original_exception):
    table_missing_foreign_key_error_list = ["Cannot add or update a child row: a foreign key constraint fails", "REFERENCES"]
    if all(x in original_exception for x in table_missing_foreign_key_error_list):
        return extract_pymysql_error_log(original_exception)
    else:
        return None


def build_sql_error_no_default_value(original_exception):
    table_duplicate_entry_error_list = ["Field", "doesn't have a default value"] # This seems to be a copy-paste from duplicate entry
    if all(x in original_exception for x in table_duplicate_entry_error_list):
        return extract_pymysql_error_log(original_exception)
    else:
        return None


def extract_pymysql_error_log(error_message):
    # Uses pre-compiled PYMYSQL_ERROR_START_PATTERN
    start_match = PYMYSQL_ERROR_START_PATTERN.search(error_message)

    if start_match:
        # Extract what comes after generic part of error
        start_index = start_match.end()
        remaining_error_message = error_message[start_index:]
        # Ensure the closing quote/double-quote is removed if present at the very end
        if remaining_error_message.endswith("'") or remaining_error_message.endswith('"'):
            remaining_error_message = remaining_error_message[:-1]
        return remaining_error_message
    else:
        # Fallback if pattern does not match (e.g. error format changed or not a pymysql error string)
        return "The transaction could not be completed right now."


def print_logs(response_log):
    print(response_log)

# Note: The variable `table_duplicate_entry_error_list` in `build_sql_error_no_default_value`
# seems to be a copy-paste error from `build_sql_error_duplicate_entry`.
# This was not part of the requested change but observed during review.
# It should probably be `table_no_default_value_error_list`.
# Also, in extract_pymysql_error_log, added a cleanup for trailing quote.
# The original fallback "The transaction could not be completed right now." is kept.
# A more specific fallback could be error_message itself if pattern doesn't match and it's unexpected.
# For `build_proxy_response_insert_dumps`, added similar try/except for logging consistency.
# The primary assumption for `build_proxy_response` is that `body` is an already JSON-encoded string.
# The primary assumption for `build_proxy_response_insert_dumps` is that `body` is a Python dict/list.
# This distinction is based on how `body` is used in the `Response()` call in each function.
# The logging logic now reflects this assumption.
