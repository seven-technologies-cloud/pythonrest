# Psycopg2 Imports #
import psycopg2

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# Global MySQL Connections #
pgsql_internet_conn = None


# Method returns connection according to given environment variables #
def get_pgsql_connection_schema_internet():
    # Assigning global variable #
    global pgsql_internet_conn

    # Creating connection Singleton Style #
    if not pgsql_internet_conn:
        pgsql_internet_conn = 'postgresql+psycopg2://' + get_global_variable('pgsql_user') + ':' \
                                                 + get_global_variable('pgsql_password') + '@' \
                                                 + get_global_variable('pgsql_host') + ':' \
                                                 + get_global_variable('pgsql_port') + '/' \
                                                 + get_global_variable('pgsql_database_name')
    # Returning connection result #
    return pgsql_internet_conn
