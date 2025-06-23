import json
import sys
from pathlib import Path

import pytest
from flask import Flask, Response

# Allow importing src package
PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.append(str(PROJECT_ROOT))

from src.e_Infra.f_Decorators.JsonLoadsDecorator import validate_json_loads_request_data
from src.e_Infra.a_Handlers.SystemMessagesHandler import get_system_message

app = Flask(__name__)


@app.route('/dummy', methods=['POST'])
@validate_json_loads_request_data
def dummy_view():
    return "success"


def call_dummy(data):
    with app.test_request_context(data=data, content_type='application/json'):
        return dummy_view()


def test_accepts_valid_json_dict():
    response = call_dummy(json.dumps({"foo": "bar"}))
    assert response == "success"


def test_accepts_valid_json_list():
    response = call_dummy(json.dumps([1, 2, 3]))
    assert response == "success"


def test_returns_401_on_invalid_json():
    response = call_dummy("{\"foo\":}")
    assert isinstance(response, Response)
    assert response.status_code == 401
    expected_body = {
        get_system_message('error_message'): get_system_message('malformed_input_data')
    }
    assert json.loads(response.get_data(as_text=True)) == expected_body

