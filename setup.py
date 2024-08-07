from setuptools import setup, find_packages

setup(
    name='pythonrest3',
    version='0.1.1',
    description='PythonRestCLI tool, created and managed by Seven Technologies Cloud.\nIt generates a complete API based on a connection string for relational databases as mysql, mssql, maria db, aurora and postgres',
    author='Seven Technologies Cloud',
    author_email='admin@seventechnologies.cloud',
    maintainer='Seven Technologies Cloud',
    keywords=['api', 'rest api', 'database', 'python', 'mysql', 'mssql', 'postgres', 'aurora', 'mariadb'],
    package_data={
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.config': ['swagger.yaml', 'redoc.html'],
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project': ['requirements.txt'],
        'pythonrest.apigenerator.resources.2 - Swagger.yaml': ['domain.yaml', 'domain_no_pk.yaml', 'sql.yaml'],
        'pythonrest.apigenerator.resources.5 - Redoc.templates': ['domain.html'],
    },
    packages=[
        'pythonrest',
        'pythonrest.domaingenerator',
        'pythonrest.databaseconnector',
        'pythonrest.apigenerator',
        'pythonrest.apigenerator.a_Domain',
        'pythonrest.apigenerator.b_Workers',
        'pythonrest.apigenerator.e_Enumerables',
        'pythonrest.apigenerator.f_Builders',
        'pythonrest.apigenerator.g_Utils',
        'pythonrest.apigenerator.resources',
        'pythonrest.apigenerator.resources.1 - Project',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.config',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.a_Presentation',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.a_Presentation.a_Domain',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.a_Presentation.b_Custom',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.a_Presentation.c_Redoc',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.a_Presentation.d_Swagger',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.a_DTO',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.a_DTO.a_Request',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.a_DTO.b_Response',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.b_Service',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.b_Service.a_Domain',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.b_Service.b_Custom',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.b_Application.b_Service.d_Swagger',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.c_Domain',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.d_Repository',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.d_Repository.a_Domain',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.d_Repository.b_Transactions',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.d_Repository.d_DbConnection',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.a_Handlers',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.b_Builders',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.b_Builders.a_Swagger',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.c_Resolvers',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.d_Validators',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.d_Validators.a_Domain',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.e_Mappers',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.f_Decorators',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.e_Infra.f_Decorators.a_DTO',
        'pythonrest.apigenerator.resources.1 - Project.1 - BaseProject.Project.src.g_Tests',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.conn_resolvers',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.conn_resolvers.mariadb',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.conn_resolvers.mssql',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.conn_resolvers.mysql',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.conn_resolvers.pgsql',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.database_conn_files',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.database_conn_files.mariadb',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.database_conn_files.mssql',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.database_conn_files.mysql',
        'pythonrest.apigenerator.resources.1 - Project.2 - Database.database_conn_files.pgsql',
        'pythonrest.apigenerator.resources.1 - Project.3 - ClassGeneric',
        'pythonrest.apigenerator.resources.2 - Swagger',
        'pythonrest.apigenerator.resources.2 - Swagger.GenericBuilder',
        'pythonrest.apigenerator.resources.2 - Swagger.GenericController',
        'pythonrest.apigenerator.resources.2 - Swagger.yaml',
        'pythonrest.apigenerator.resources.3 - Variables',
        'pythonrest.apigenerator.resources.3 - Variables.EnvironmentVariablesFile',
        'pythonrest.apigenerator.resources.4 - SQLRoute',
        'pythonrest.apigenerator.resources.5 - Redoc',
        'pythonrest.apigenerator.resources.5 - Redoc.GenericController',
        'pythonrest.apigenerator.resources.5 - Redoc.templates',
    ],
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
        'pyinstaller==6.3.0',
    ],
    entry_points={
        'console_scripts': [
            'pythonrest=pythonrest:app',
        ],
    },
)