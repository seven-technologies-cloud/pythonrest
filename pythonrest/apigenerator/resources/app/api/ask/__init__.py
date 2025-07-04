from flask import Blueprint

bp = Blueprint('ask', __name__)

from pythonrest.apigenerator.resources.app.api.ask import routes # Or app.api.ask if structure changes during generation
