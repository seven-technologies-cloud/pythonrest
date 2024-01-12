import os
import sys

# Set the working directory to the location of the __init__.py file of the framework
os.environ['PACKAGE_DIR'] = os.path.abspath(os.path.dirname(__file__))

# Append the __init__.py folder to pythonpath to resolve imports and retrieving of files
sys.path.append(os.environ['PACKAGE_DIR'])

# Import your main application
from .pythonrest import app
