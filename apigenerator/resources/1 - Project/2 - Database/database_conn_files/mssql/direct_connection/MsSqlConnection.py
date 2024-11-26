# PyMssql Imports #
import pymssql

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# Global MySQL Connections #
mssql_internet_conn = None


# Method returns connection according to given environment variables #
def get_mssql_connection_schema_internet():
    # Assigning global variable #
    global mssql_internet_conn

    # Creating connection Singleton Style #
    if not mssql_internet_conn:
        mssql_internet_conn = 'mssql+pymssql://' + get_global_variable('mssql_user') + ':' \
                                                 + get_global_variable('mssql_password') + '@' \
                                                 + get_global_variable('mssql_host') + ':' \
                                                 + get_global_variable('mssql_port') + '/' \
                                                 + get_global_variable('mssql_schema')
    # Returning connection result #
    return mssql_internet_conn
