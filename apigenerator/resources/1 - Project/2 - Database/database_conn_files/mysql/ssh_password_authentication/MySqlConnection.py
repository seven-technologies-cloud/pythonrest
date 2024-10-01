# PyMysql Imports #
import pymysql
from sshtunnel import SSHTunnelForwarder

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# Global MySQL Connections #
tunnel = None

# Method returns connection according to given environment variables #
def get_mysql_connection_schema_internet():
    # Assigning global variable #
    global tunnel

    # Creating connection Singleton Style #
    if not tunnel:

        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(get_global_variable('ssh_host'), int(get_global_variable('ssh_port'))),
            ssh_username=get_global_variable('ssh_user'),
            ssh_password=get_global_variable('ssh_password'),
            remote_bind_address=(get_global_variable('mysql_host'), int(get_global_variable('mysql_port'))),
            local_bind_address=(get_global_variable('ssh_host'), int(get_global_variable('ssh_local_bind_port'))),
            set_keepalive=10
        )

        tunnel.start()

        mysql_conn_string = 'mysql+pymysql://' + get_global_variable('mysql_user') + ':' \
                                                 + get_global_variable('mysql_password') + '@' \
                                                 + get_global_variable('mysql_host') + ':' \
                                                 + str(tunnel.local_bind_port) + '/' \
                                                 + get_global_variable('mysql_schema')
    # Returning connection result #
    return mysql_conn_string
