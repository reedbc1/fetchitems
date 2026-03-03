import os
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from dotenv import load_dotenv
import pymysql
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, Text
from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import delete
from sqlalchemy import ForeignKey


# Load .env file
load_dotenv()

def connect_with_connector() -> sqlalchemy.engine.base.Engine:
    """
    Initializes a connection pool for a Cloud SQL instance of MySQL.

    Uses the Cloud SQL Python Connector package.
    """
    # Note: Saving credentials in environment variables is convenient, but not
    # secure - consider a more secure solution such as
    # Cloud Secret Manager (https://cloud.google.com/secret-manager) to help
    # keep secrets safe.

    instance_connection_name = os.environ[
        "INSTANCE_CONNECTION_NAME"
    ]  # e.g. 'project:region:instance'
    db_user = os.environ["DB_USER"]  # e.g. 'my-db-user'
    db_pass = os.environ["DB_PASS"]  # e.g. 'my-db-password'
    db_name = "items"

    ip_type = IPTypes.PRIVATE if os.environ.get("PRIVATE_IP") else IPTypes.PUBLIC

    # initialize Cloud SQL Python Connector object
    connector = Connector(ip_type=ip_type, refresh_strategy="LAZY")

    def getconn() -> pymysql.connections.Connection:
        conn: pymysql.connections.Connection = connector.connect(
            instance_connection_name,
            "pymysql",
            user=db_user,
            password=db_pass,
            db=db_name,
        )
        return conn

    engine = sqlalchemy.create_engine(
        "mysql+pymysql://",
        creator=getconn,
        # ...
    )
    return engine


metadata_obj = MetaData()

dvd_table = Table(
    "dvd_format",
    metadata_obj,
    Column("id", String, primary_key=True),
    Column("title", String),
    Column("publicationDate", String),
    Column("coverUrl", Text),
    Column("editionId", String, ForeignKey("dvd_editions.id"), nullable=False)
)

print(dvd_table.c.keys())

dvd_editions = Table(
    "dvd_editions",
    metadata_obj,
    Column("id", String, primary_key=True),
    Column("genre", String),
    Column("actors", String)
)

print(dvd_editions.c.keys())

engine = connect_with_connector()

"""Create tables"""
# metadata_obj.create_all(engine)

    
    


    










