# System Imports #
import os

# Importing Flask #
from flask import Flask, Blueprint, render_template, redirect, url_for, request, flash, session

# Infra Imports #
from src.e_Infra.b_Builders.a_Swagger.SwaggerBuilder import *


# Initializing Flask #
app_handler = Flask(__name__)
app_handler.template_folder = os.path.join(os.getcwd(), 'config')

# Creating Redoc blueprint #
redoc_blueprint = Blueprint('redoc', __name__)

# Creating FlaskAdminPanel blueprint #
auth_blueprint = Blueprint('auth', __name__)

# Building Swagger Blueprint #
build_swagger_blueprint(app_handler)
