from setuptools import setup
import os


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
    version='0.2.6',
    description='A CLI tool that generates a complete API using a connection string for supported databases: mysql, mssql, mariadb and postgres',
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
