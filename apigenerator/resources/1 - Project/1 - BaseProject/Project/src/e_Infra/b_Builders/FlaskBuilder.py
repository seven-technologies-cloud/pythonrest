# Importing Flask #
from flask import Flask

# Infra Imports #
from src.e_Infra.b_Builders.a_Swagger.SwaggerBuilder import *

# Initialing FlaskLambda #
app_handler = Flask(__name__)

# Building Swagger Blueprint #
build_swagger_blueprint(app_handler)
