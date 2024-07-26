# System Imports #
import os

# Importing Flask #
from flask import Flask, Blueprint

# Infra Imports #
from src.e_Infra.b_Builders.a_Swagger.SwaggerBuilder import *
from src.a_Presentation.c_Redoc.RedocController import *


# Initializing Flask #
app_handler = Flask(__name__, template_folder=os.path.join(os.getcwd(), 'config'))

# Creating Redoc blueprint #
redoc_blueprint = Blueprint('redoc', __name__)

# Building Swagger Blueprint #
build_swagger_blueprint(app_handler)


# Building Redoc Blueprint #
build_redoc_blueprint(app_handler, redoc_blueprint)
