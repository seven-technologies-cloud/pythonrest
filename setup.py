from setuptools import setup, find_packages

setup(
    name='pythonrest3',
    version='0.1.0',
    description='PythonRestCLI tool, created and managed by Seven Technologies Cloud.\nIt generates a complete API based on a connection string for relational databases as mysql, mssql, maria db, aurora and postgres',
    author='Seven Technologies Cloud',
    author_email='admin@seventechnologies.cloud',
    maintainer='Seven Technologies Cloud',
    keywords=['api', 'rest api', 'database', 'python', 'mysql', 'mssql', 'postgres', 'aurora', 'mariadb'],
    packages=find_packages(),
    install_requires=[
        'typer==0.9.0',
        'PyYAML==6.0.1',
        'parse==1.20.0',
        'mergedeep==1.3.4',
        'pymysql==1.1.0',
        'psycopg2-binary==2.9.9',
        'pymssql==2.2.10',
        'pyinstaller==6.3.0',
    ],
    entry_points={
        'console_scripts': [
            'pythonrest=pythonrest:app',
        ],
    },
)
