# System imports #
import traceback

# Infra Imports #
from src.e_Infra.b_Builders.ProxyResponseBuilder import *
from src.e_Infra.GlobalVariablesManager import *
from src.e_Infra.a_Handlers.SystemMessagesHandler import *


# Main method #
def handle_custom_exception(exception):

    # Defining default status code and retrieving errors from generic exception #
    status_code = 400

    # Validating status codes #
    if hasattr(exception, 'response'):
        if 'Error' in exception.response:
            if 'Code' in exception.response['Error']:
                if exception.response['Error']['Code'] == 'BadRequest':
                    status_code = 400
                elif exception.response['Error']['Code'] == 'Unauthorized':
                    status_code = 401
                elif exception.response['Error']['Code'] == 'Forbidden':
                    status_code = 403
                elif exception.response['Error']['Code'] == 'NotFound':
                    status_code = 404
                elif exception.response['Error']['Code'] == 'UserNotFoundException':
                    status_code = 404
                elif exception.response['Error']['Code'] == 'ResourceNotFoundException':
                    status_code = 404
                elif exception.response['Error']['Code'] == 'MethodNotAllowed':
                    status_code = 405
                elif exception.response['Error']['Code'] == 'NotAcceptable':
                    status_code = 406
                elif exception.response['Error']['Code'] == 'RequestTimeout':
                    status_code = 408
                elif exception.response['Error']['Code'] == 'Conflict':
                    status_code = 409
                elif exception.response['Error']['Code'] == 'Gone':
                    status_code = 410
                elif exception.response['Error']['Code'] == 'LengthRequired':
                    status_code = 411
                elif exception.response['Error']['Code'] == 'PreconditionFailed':
                    status_code = 412
                elif exception.response['Error']['Code'] == 'RequestEntityTooLarge':
                    status_code = 413
                elif exception.response['Error']['Code'] == 'RequestURITooLarge':
                    status_code = 414
                elif exception.response['Error']['Code'] == 'UnsupportedMediaType':
                    status_code = 415
                elif exception.response['Error']['Code'] == 'RequestedRangeNotSatisfiable':
                    status_code = 416
                elif exception.response['Error']['Code'] == 'ExpectationFailed':
                    status_code = 417
                elif exception.response['Error']['Code'] == 'ImATeapot':
                    status_code = 418
                elif exception.response['Error']['Code'] == 'UnprocessableEntity':
                    status_code = 422
                elif exception.response['Error']['Code'] == 'Locked':
                    status_code = 423
                elif exception.response['Error']['Code'] == 'FailedDependency':
                    status_code = 424
                elif exception.response['Error']['Code'] == 'PreconditionRequired':
                    status_code = 428
                elif exception.response['Error']['Code'] == 'RequestHeaderFieldsTooLarge':
                    status_code = 431
                elif exception.response['Error']['Code'] == 'UnavailableForLegalReasons':
                    status_code = 451
                elif exception.response['Error']['Code'] == 'InternalServerError':
                    status_code = 500
                elif exception.response['Error']['Code'] == 'NotImplemented':
                    status_code = 501
                elif exception.response['Error']['Code'] == 'BadGateway':
                    status_code = 502
                elif exception.response['Error']['Code'] == 'ServiceUnavailable':
                    status_code = 503
                elif exception.response['Error']['Code'] == 'GatewayTimeout':
                    status_code = 504
                elif exception.response['Error']['Code'] == 'HTTPVersionNotSupported':
                    status_code = 505

    # Creating response body #
    body = get_system_empty_dict()
    body['ErrorMessage'] = str(exception)

    # Assembling response body according to stack_trace_enabled attribute
    if get_global_variable('display_stacktrace_on_error') == "True":
        trace = traceback.format_exc()
        body['Trace'] = trace.replace('\"', "'").split("\n")
        body['ErrorType'] = type(exception).__name__

    # Returning formatted json #
    return build_proxy_response_insert_dumps(status_code, body)


# Method to handle repository exception #
def handle_repository_exception(exception):
    # Validating Database error #
    if hasattr(exception, 'orig'):
        # Returning Database error #
        return [arg.decode() if isinstance(arg, bytes) else arg for arg in exception.orig.args if type(arg) != int]
    # Returning Generic error #
    return [arg.replace("'<class ", '').replace(">'", '') for arg in exception.args if type(arg) != int]
