# System Imports #
import json
import re

# Infra Imports #
from src.e_Infra.CustomVariables import *
from src.e_Infra.GlobalVariablesManager import *

# Flask Imports #
from flask import Response


# Method builds a response with json.dumps and adding error list attribute #
def build_proxy_response_insert_dumps_error_list(status_code, error_message_list):
    # Building error final list structure #
    error_list = get_system_empty_dict()
    if error_message_list != get_system_empty_list():
        error_list['error_list'] = error_message_list
    # Returning error list as an API built response #
    return build_proxy_response_insert_dumps(status_code, error_list)


# Method builds a clean json response #
def build_proxy_response(status_code, body):
    try:
        try:
            print_logs(json.dumps({"statusCode": status_code, "body": json.loads(json.dumps(body))}, default=str))
        except:
            print_logs(json.dumps({"statusCode": status_code, "body": json.loads(body)}, default=str))
    except:
        print_logs('Log failed', default=str)
    
    return Response(response=body, status=status_code, content_type='application/json')



# Method builds a response with json.dumps #
def build_proxy_response_insert_dumps(status_code, body):
    response_body = json.dumps(body, sort_keys=True, default=str)

    print_logs(json.dumps({
        "statusCode": status_code,
        "body": body
    }, default=str))

    return Response(
        response=response_body,
        status=status_code,
        content_type='application/json'
    )


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
    table_duplicate_entry_error_list = ["Field", "doesn't have a default value"]
    if all(x in original_exception for x in table_duplicate_entry_error_list):
        return extract_pymysql_error_log(original_exception)
    else:
        return None


def extract_pymysql_error_log(error_message):
    # Regular expression to match generic part of pymysql err Error and the error code next
    start_pattern = r"\(pymysql\.err\.[\w]+\) \([\d]+, [\"']"

    start_match = re.search(start_pattern, error_message)

    if start_match:
        # Extract what comes after generic part of error
        start_index = start_match.end()
        remaining_error_message = error_message[start_index:]
        return remaining_error_message
    else:
        return "The transaction could not be completed right now."


def print_logs(response_log):
    print(response_log)
