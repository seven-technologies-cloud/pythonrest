from setuptools import setup, find_packages
import os


def find_packages_custom(directory='.', exclude=(), prefix='pythonrest'):
    yield prefix
    for root, dirs, files in os.walk(directory):
        dirs[:] = [d for d in dirs if d not in exclude]
        if '__init__.py' in files:
            package_path = f"{prefix}.{os.path.relpath(root, directory).replace(os.sep, '.')}"
            if package_path != f"{prefix}..":
                yield package_path

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

# Include requirements.txt in package_data
package_data = list_files_by_extension(extension=('.yaml', '.txt', '.html', '.md'))
package_data['pythonrest'] = ['requirements.txt']

setup(
    name='pythonrest3',
    version='0.1.3',
    description='PythonRestCLI tool, created and managed by Seven Technologies Cloud.\nIt generates a complete API based on a connection string for relational databases as mysql, mssql, maria db, aurora and postgres',
    author='Seven Technologies Cloud',
    author_email='admin@seventechnologies.cloud',
    maintainer='Seven Technologies Cloud',
    keywords=['api', 'rest api', 'database', 'python',
              'mysql', 'mssql', 'postgres', 'aurora', 'mariadb'],
    package_data=list_files_by_extension(extension=('.yaml', '.txt', '.html', '.md')),
    packages=list(find_packages_custom(exclude=['venv'])),
    package_dir={'pythonrest': '.'},
    install_requires=[],
    entry_points={
        'console_scripts': [
            'pythonrest=pythonrest:app',
        ],
    },
)