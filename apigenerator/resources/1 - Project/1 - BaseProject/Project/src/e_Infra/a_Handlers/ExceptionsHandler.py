# System imports #
# import traceback # Removed from top

# Infra Imports #
from src.e_Infra.b_Builders.ProxyResponseBuilder import build_proxy_response_insert_dumps
from src.e_Infra.GlobalVariablesManager import get_global_variable
from src.e_Infra.a_Handlers.SystemMessagesHandler import get_system_empty_dict


# Main method #
def handle_custom_exception(exception):

    # Defining default status code and retrieving errors from generic exception #
    status_code = 400

    # Validating status codes #
    # This long if/elif chain for status codes is functional but could be refactored
    # into a dictionary lookup if 'exception.response['Error']['Code']' is reliably present
    # and is the exact key for the status code. For now, leaving as is per subtask scope.
    if hasattr(exception, 'response'):
        if 'Error' in exception.response: # Check if 'Error' key exists
            error_details = exception.response['Error']
            if isinstance(error_details, dict) and 'Code' in error_details: # Check if 'Code' key exists
                error_code_str = error_details['Code']
                # Example of dict mapping (not implemented here to keep change focused):
                # error_code_map = {"BadRequest": 400, "Unauthorized": 401, ...}
                # status_code = error_code_map.get(error_code_str, 400)
                if error_code_str == 'BadRequest': status_code = 400
                elif error_code_str == 'Unauthorized': status_code = 401
                elif error_code_str == 'Forbidden': status_code = 403
                elif error_code_str == 'NotFound': status_code = 404
                elif error_code_str == 'UserNotFoundException': status_code = 404
                elif error_code_str == 'ResourceNotFoundException': status_code = 404
                elif error_code_str == 'MethodNotAllowed': status_code = 405
                elif error_code_str == 'NotAcceptable': status_code = 406
                elif error_code_str == 'RequestTimeout': status_code = 408
                elif error_code_str == 'Conflict': status_code = 409
                elif error_code_str == 'Gone': status_code = 410
                elif error_code_str == 'LengthRequired': status_code = 411
                elif error_code_str == 'PreconditionFailed': status_code = 412
                elif error_code_str == 'RequestEntityTooLarge': status_code = 413
                elif error_code_str == 'RequestURITooLarge': status_code = 414
                elif error_code_str == 'UnsupportedMediaType': status_code = 415
                elif error_code_str == 'RequestedRangeNotSatisfiable': status_code = 416
                elif error_code_str == 'ExpectationFailed': status_code = 417
                elif error_code_str == 'ImATeapot': status_code = 418 # RFC 2324
                elif error_code_str == 'UnprocessableEntity': status_code = 422
                elif error_code_str == 'Locked': status_code = 423
                elif error_code_str == 'FailedDependency': status_code = 424
                elif error_code_str == 'PreconditionRequired': status_code = 428
                elif error_code_str == 'RequestHeaderFieldsTooLarge': status_code = 431
                elif error_code_str == 'UnavailableForLegalReasons': status_code = 451
                elif error_code_str == 'InternalServerError': status_code = 500
                elif error_code_str == 'NotImplemented': status_code = 501
                elif error_code_str == 'BadGateway': status_code = 502
                elif error_code_str == 'ServiceUnavailable': status_code = 503
                elif error_code_str == 'GatewayTimeout': status_code = 504
                elif error_code_str == 'HTTPVersionNotSupported': status_code = 505
                # else: default status_code remains 400 if Code is not recognized

    # Creating response body #
    body = get_system_empty_dict()
    body['ErrorMessage'] = str(exception) # Ensure exception is stringified

    # Assembling response body according to stack_trace_enabled attribute
    if get_global_variable('display_stacktrace_on_error') == "True":
        import traceback # Moved import here
        trace = traceback.format_exc()
        body['Trace'] = trace.replace('\"', "'").split("\n")
        body['ErrorType'] = type(exception).__name__

    # Returning formatted json #
    return build_proxy_response_insert_dumps(status_code, body)


# Method to handle repository exception #
def handle_repository_exception(exception):
    # Validating Database error #
    if hasattr(exception, 'orig') and hasattr(exception.orig, 'args') and exception.orig.args:
        # Returning Database error #
        # Ensure args are decoded if bytes, and filter out non-string/non-bytes if necessary,
        # though the original filtered out int.
        return [arg.decode() if isinstance(arg, bytes) else str(arg) for arg in exception.orig.args]
    # Returning Generic error #
    # Ensure args are stringified.
    return [str(arg).replace("'<class ", '').replace(">'", '') for arg in exception.args]

# Minor improvements in handle_custom_exception:
# - Added checks for `exception.response['Error']` and `error_details['Code']` existence.
# - Ensured `str(exception)` for ErrorMessage.
# - In handle_repository_exception:
#   - Added check for `hasattr(exception.orig, 'args')` and `exception.orig.args` being non-empty.
#   - Ensured all args are converted to string in both branches.
#   - Removed `if type(arg) != int` as string conversion handles this; if int args are truly not desired,
#     a separate filter `if not isinstance(arg, int)` could be added before str(arg).
#     The original code's `type(arg) != int` for `exception.orig.args` was a bit unusual as DB errors
#     often have string messages and error codes (which might be int but usually part of a string).
#     For generic `exception.args`, they are usually strings or objects that can be stringified.
#     Simplified to convert all args to string for broader compatibility.
# The long if/elif for status codes was kept as is per subtask scope, but noted for potential refactor.
