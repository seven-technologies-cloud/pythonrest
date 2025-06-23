import json
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace

# Prevent importing heavy root package dependencies
pythonrest_stub = ModuleType('pythonrest.pythonrest')
pythonrest_stub.app = None
sys.modules['pythonrest.pythonrest'] = pythonrest_stub
pythonrest_pkg = ModuleType('pythonrest')
pythonrest_pkg.__path__ = []
pythonrest_pkg.pythonrest = pythonrest_stub
sys.modules['pythonrest'] = pythonrest_pkg

apigenerator_pkg = ModuleType('pythonrest.apigenerator')
apigenerator_pkg.__path__ = []
sys.modules['pythonrest.apigenerator'] = apigenerator_pkg

resources_pkg = ModuleType('pythonrest.apigenerator.resources')
resources_pkg.__path__ = []
sys.modules['pythonrest.apigenerator.resources'] = resources_pkg

# Stub minimal flask module to avoid external dependency
class DummyResponse:
    def __init__(self, response=None, status=200, content_type=None):
        self.response = response
        self.status_code = status
        self.content_type = content_type

    def get_data(self, as_text=False):
        return self.response if as_text else self.response

flask_stub = ModuleType('flask')
flask_stub.Response = DummyResponse
flask_stub.request = SimpleNamespace(data=b'')

sys.modules['flask'] = flask_stub

# Allow importing src package
PROJECT_ROOT = Path(__file__).resolve().parents[4]
sys.path.append(str(PROJECT_ROOT))

from src.e_Infra.f_Decorators.JsonLoadsDecorator import validate_json_loads_request_data
from src.e_Infra.a_Handlers.SystemMessagesHandler import get_system_message


@validate_json_loads_request_data
def dummy_view():
    return "success"


def call_dummy(raw_data):
    flask_stub.request.data = raw_data
    return dummy_view()


def test_accepts_valid_json_dict():
    response = call_dummy(json.dumps({"foo": "bar"}).encode())
    assert response == "success"


def test_accepts_valid_json_list():
    response = call_dummy(json.dumps([1, 2, 3]).encode())
    assert response == "success"


def test_rejects_invalid_json():
    response = call_dummy(b'{"foo":}')
    assert isinstance(response, DummyResponse)
    assert response.status_code == 401
    expected = {get_system_message('error_message'): get_system_message('malformed_input_data')}
    assert json.loads(response.get_data(as_text=True)) == expected


def test_rejects_non_object_json():
    response = call_dummy(json.dumps(1).encode())
    assert isinstance(response, DummyResponse)
    assert response.status_code == 401
    expected = {get_system_message('error_message'): get_system_message('malformed_input_data')}
    assert json.loads(response.get_data(as_text=True)) == expected
