# Infra Imports #
from src.e_Infra.GlobalVariablesManager import *

# MsSqlConnection Imports #
import sqlalchemy as sa
from sqlalchemy.orm import scoped_session, sessionmaker

# MySQL Connection Imports #
from src.d_Repository.d_DbConnection.MsSqlConnection import *

# Global MsSql Session #
session = None


# Method retrieves database connection according to selected environment #
def get_mssql_connection_session():

    # Assigning global variable #
    global session

    # Creating session #
    if session is None:
        # This block creates engine and session for the database #
            conn = get_mssql_connection_schema_internet()
            engine = sa.create_engine(conn)
            session = scoped_session(sessionmaker(bind=engine))

    # Returning session #
    return session
