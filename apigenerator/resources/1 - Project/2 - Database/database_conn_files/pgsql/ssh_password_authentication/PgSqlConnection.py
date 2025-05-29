# Psycopg2 Imports #
import psycopg2
from sshtunnel import SSHTunnelForwarder

# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# Global MySQL Connections #
tunnel = None

# Method returns connection according to given environment variables #
def get_pgsql_connection_schema_internet():
    # Assigning global variable #
    global tunnel

    # Creating connection Singleton Style #
    if not tunnel:

        tunnel = SSHTunnelForwarder(
            ssh_address_or_host=(get_global_variable('ssh_host'), int(get_global_variable('ssh_port'))),
            ssh_username=get_global_variable('ssh_user'),
            ssh_password=get_global_variable('ssh_password'),
            remote_bind_address=(get_global_variable('pgsql_host'), int(get_global_variable('pgsql_port'))),
            local_bind_address=(get_global_variable('ssh_host'), int(get_global_variable('ssh_local_bind_port'))),
            set_keepalive=10
        )

        tunnel.start()

        pgsql_conn_string = 'postgresql+psycopg2://' + get_global_variable('pgsql_user') + ':' \
                              + get_global_variable('pgsql_password') + '@' \
                              + get_global_variable('pgsql_host') + ':' \
                              + str(tunnel.local_bind_port) + '/' \
                              + get_global_variable('pgsql_database_name')

    # Returning connection result #
    return pgsql_conn_string
