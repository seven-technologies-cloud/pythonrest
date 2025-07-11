from setuptools import setup
import os

def read_file(filename):
    with open(filename, encoding="utf-8") as f:
        return f.read()

def find_packages_custom(start_directory='.', include=None, prefix='pythonrest'):
    if include is None:
        include = [start_directory]

    packages = [prefix]
    for dir in include:
        for root, dirs, files in os.walk(dir):
            if '__init__.py' in files:
                package_path = f"{prefix}.{os.path.relpath(root, start_directory).replace(os.sep, '.')}"
                packages.append(package_path)
    return packages


def list_files_by_extension(directory='.', extension=()):
    package_data = {}
    for root, dirs, files in os.walk(directory):
        relative_path = os.path.relpath(root, directory)
        if 'apigenerator/resources/' in relative_path.replace(os.sep, '/'):
            values = [file for file in files if file.endswith(extension)]
            if values:
                new_path = 'pythonrest/' + \
                    relative_path.replace(os.sep, '/')
                new_path = new_path.replace('/', '.')
                package_data[new_path] = values
    return package_data

setup(
    name='pythonrest3',
    version='0.3.7',
    description='A CLI tool that generates a complete API using a connection string for supported databases: mysql, mssql, mariadb and postgres',
    long_description=(
        "# PythonREST\n\n"
        "PythonREST is the ultimate full API generator for Python language. Based on the best performing frameworks "
        "and software development best practices, PythonREST can create an entire CRUD API in minutes or seconds "
        "based on your relational database on a single CLI command. This allows you to create your APIs from scratch "
        "and update your current API previously created with our tool to always match your latest database definitions.\n\n"
        "**THIS WILL SAVE YOU MONTHS OF DEVELOPMENT TIME, GUARANTEED!**\n\n"
        "Your new generated API will have full CRUD compatibility with your mapped database and full Swagger "
        "documentation and specs available. With your new API in hand, you will be able to containerize or serverless "
        "deploy it to any local, private, and public cloud providers of your choice and use it at will! If you're "
        "interested in taking your API to the next level and don't know how, please inquire with us at the email below "
        "for consultancy services.\n\n"
        "This project is under active enhancement, and we have several open GitHub issues to improve it further. "
        "If you're an Open Source enthusiast and wish to contribute, we'd be more than happy to have you on our team! "
        "Get in touch via [admin@seventechnologies.cloud](mailto:admin@seventechnologies.cloud) if you have any doubts "
        "or suggestions, and don't forget to star our repository!\n\n"
        "### If you like our solution, please consider donating on our "
        "[Patreon campaign](https://www.patreon.com/seventechnologies)!\n\n"
        "## Version Disclaimer\n\n"
        "**Version 0.2.1**\n"
        "* Added some quality of life improvements for Redoc building\n\n"
        "**Version 0.2.4**\n"
        "* Adding SSH and SSL connection methods (direct file provision only where applicable)\n"
        "* Support for PostgreSQL MONEY type (mapped as a string in code)\n"
        "* Implementation of GROUPBY SQL Statement as a header for table routes\n\n"
        "**Version 0.2.6**\n"
        "* Support for column names that contain unusual characters like '-', ' ', '.', '/', '\\', ':', '~', '*', '+', '|', '@'\n\n"
        "**Version 0.2.7**\n"
        "* SQL Views are no longer listed as routes in the generated API\n"
        "* Fixing some cases where exceptions were improperly returned as byte-like objects\n"
        "* Fixing `[or]` filter in GET routes when using multiple query parameters simultaneously\n"
        "* Improving rendering of Swagger and Redoc pages\n\n"
        "**Version 0.2.8**\n"
        "* Small fixes to swagger improved rendering\n\n"
        "**Version 0.2.9**\n"
        "* Support for columns named with Python reserved keywords\n\n"
        "**Version 0.3.0**\n"
        "* Adding fixed version for generated API libraries to avoid breaking changes\n\n"
        "**Version 0.3.1**\n"
        "* Setting READ COMMITTED isolation level on mysql and mariadb resolvers\n\n"
        "**Version 0.3.2**\n"
        "* Adding fix for search path option not working on some PostgreSQL environments\n\n"
        "**Version 0.3.3**\n"
        "* Adding powershell test scripts for mysql, postgresql and sqlserver\n\n"
        "**Version 0.3.4**\n"
        "* Fix CORS issue by properly configuration of after request decorator function.\n\n"
        "**Version 0.3.5**\n"
        "* Synchronization between the versions on PyPI and the releases on GitHub.\n\n"
        "**Version 0.3.6**\n"
        "* Introduced Model Context Protocol (MCP) endpoints for dynamic LLM configuration and interaction.\n\n"
        "**Version 0.3.7**\n"
        "* Adding metadata to reserved keyword formatter.\n"
    ),
    long_description_content_type="text/markdown",
    author='Seven Technologies Cloud',
    author_email='admin@seventechnologies.cloud',
    maintainer='Seven Technologies Cloud',
    keywords=['api', 'rest api', 'database', 'python',
              'mysql', 'mssql', 'postgres', 'aurora', 'mariadb'],
    package_data=list_files_by_extension(
        extension=('.yaml', '.txt', '.html', '.md')),
    packages=find_packages_custom(
        include=['apigenerator', 'databaseconnector', 'domaingenerator']),
    package_dir={'pythonrest': '.'},
    install_requires=[
        'typer==0.9.0',
        'PyYAML==6.0.1',
        'parse==1.20.0',
        'mergedeep==1.3.4',
        'pymysql==1.1.0',
        'rsa==4.9',
        'cryptography==42.0.7',
        'cffi==1.16.0',
        'pycparser==2.22',
        'pyasn1==0.6.0',
        'psycopg2-binary==2.9.9',
        'pymssql==2.2.11',
        'sshtunnel==0.4.0',
    ],
    entry_points={
        'console_scripts': [
            'pythonrest=pythonrest:app',
        ],
    },
)
