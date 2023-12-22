# System Imports #
import json

# Infra Imports #
from src.e_Infra.CustomVariables import *

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
    print_logs(json.dumps({"statusCode": status_code, "body": body}, default=str))
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


def print_logs(response_log):
    print(response_log)
