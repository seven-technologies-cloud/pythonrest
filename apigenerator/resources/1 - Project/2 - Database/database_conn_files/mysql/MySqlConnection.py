# PyMysql Imports #
import pymysql

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# Global MySQL Connections #
mysql_internet_conn = None


# Method returns connection according to given environment variables #
def get_mysql_connection_schema_internet():
    # Assigning global variable #
    global mysql_internet_conn

    # Creating connection Singleton Style #
    if not mysql_internet_conn:
        mysql_internet_conn = 'mysql+pymysql://' + get_global_variable('mysql_user') + ':' \
                                                 + get_global_variable('mysql_password') + '@' \
                                                 + get_global_variable('mysql_host') + ':' \
                                                 + get_global_variable('mysql_port') + '/' \
                                                 + get_global_variable('mysql_schema')
    # Returning connection result #
    return mysql_internet_conn
