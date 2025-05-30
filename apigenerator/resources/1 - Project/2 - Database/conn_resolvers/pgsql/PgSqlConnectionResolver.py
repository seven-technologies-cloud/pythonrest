# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# PgSqlConnection Imports #
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import event

# MySQL Connection Imports #
from src.d_Repository.d_DbConnection.PgSqlConnection import *

# Global PgSql Session #
session = None


# Method retrieves database connection according to selected environment #
def get_pgsql_connection_session():

    # Assigning global variable #
    global session

    # Creating session #
    if session is None:
        # This block creates engine and session for the database #
            conn = get_pgsql_connection_schema_internet()
            engine = sa.create_engine(conn)

            schema = get_global_variable('pgsql_schema')

            @event.listens_for(engine, "connect")
            def set_search_path(dbapi_connection, connection_record):
                cursor = dbapi_connection.cursor()
                cursor.execute(f'SET search_path TO {schema}, public')
                cursor.close()

            session = scoped_session(sessionmaker(bind=engine))

    # Returning session #
    return session
