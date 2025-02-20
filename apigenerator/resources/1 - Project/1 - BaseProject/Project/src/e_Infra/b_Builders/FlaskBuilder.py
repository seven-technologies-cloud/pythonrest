# System Imports #
import os

# Importing Flask #
from flask import Flask, Blueprint, render_template_string, render_template, redirect, url_for, request, flash, session


# Initializing Flask #
app_handler = Flask(__name__)
app_handler.template_folder = os.path.join(os.getcwd(), 'config')

# Creating FlaskAdminPanel blueprint #
auth_blueprint = Blueprint('auth', __name__)
