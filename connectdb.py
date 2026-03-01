import os
from google.cloud.sql.connector import Connector, IPTypes
import sqlalchemy
from dotenv import load_dotenv
import pymysql
from fetchitems import get_data
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String
from sqlalchemy import text
from sqlalchemy import insert
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy import delete


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


# connect engine
engine = connect_with_connector()

# define metadata_obj
metadata_obj = MetaData()

# init books table
books = Table("books", metadata_obj, autoload_with=engine)

# fetch and load records
records = get_data()

# all fetched ids
ids = {item['id'] for item in records}

# check to see if any records already exist in db
stmt = select(books.c.id)

with Session(engine) as session:
    for row in session.execute(stmt):
        if row[0] in ids:
            ids.remove(row[0])
        else:
            # delete row in db where id = row[0]
            stmt = delete(books).where(books.c.id == row[0])
            session.execute(stmt)
    session.commit()
    
filtered_records = [r for r in records if r['id'] in ids]

# insert records not already in db
with Session(engine) as session:
    result = session.execute(
        insert(books), filtered_records
    )
    session.commit()

    
    


    









# with engine.connect() as conn:
#     result = conn.execute("SELECT id FROM books")
# print(result)

# with engine.connect() as conn:
#     result = conn.execute(
#         insert(books), records
#     )
#     conn.commit()
