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
import logging
from fetchdvds import format_groups, get_edition
import asyncio
from asynciolimiter import Limiter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

dvd_format = Table(
    "dvd_format",
    metadata_obj,
    Column("id", String(200), primary_key=True),
    Column("title", String(200)),
    Column("publicationDate", String(50)),
    Column("coverUrl", Text),
    Column("editionId", String(200), nullable=False)
)

dvd_editions = Table(
    "dvd_editions",
    metadata_obj,
    Column("id", String(200), primary_key=True),
    Column("genre", String(200)),
    Column("actors", String(500))
)

"""Create tables"""
# engine = connect_with_connector()
# metadata_obj.create_all(engine)

def update_table(engine):
    logger.info("Starting update operations...")
    with engine.connect() as conn:
        stmt = select(dvd_format.c.id)
        for row in conn.execute(stmt):
            print(row)

def initialize_dvds(engine):
    logger.info("Starting DVD initialization...")
    with engine.connect() as conn:
        conn.execute(
            insert(dvd_format),
            format_groups(),
        )
        conn.commit()

def update_dvds(engine):
    """Remove DVDs that are no longer in the API and add new ones"""

    # 1. Get all existing DVD IDs from the database
    logger.info("Starting DVD updates...")
    with engine.connect() as conn:
        stmt = select(dvd_format.c.id)
        existing_ids = set()
        for row in conn.execute(stmt):
            existing_ids.add(row[0])
        
        logger.info(f"Found {len(existing_ids)} existing DVD IDs in the database.")
        # 2. Fetch new DVD data from the API
        new_dvds = format_groups()
        for dvd in new_dvds:
            if dvd['id'] not in existing_ids:
                conn.execute(
                    insert(dvd_format),
                    dvd
                )

        # 3. Remove DVDs that are no longer in the API
        for id in existing_ids:
            if id not in [dvd['id'] for dvd in new_dvds]:
                conn.execute(
                    delete(dvd_format),
                    {"id": id}
                )

        conn.commit()

### Functions for updating format_dvd table ###

def fetch_dvd_data():
    # 1. Fetch DVD data from the API
    logger.info("Calling Vega API...")
    try:
        data = format_groups()
        return data
    
    except Exception as e:
        logger.exception(f"An exception occured: {e}")
        raise Exception("Vega API call was unsuccessful")

def generate_dif_d(engine, data):
    # 2. Generate diff
    #   a. to_insert, to_delete, unchanged
    #   b. Log diff

    logger.info("Fetching data from table...")

    # get existing ids
    with engine.connect() as conn:
        stmt = select(dvd_format.c.id)
        existing_ids = set()
        for row in conn.execute(stmt):
            existing_ids.add(row[0])

    # get API ids
    new_ids = set()
    for record in data:
        new_ids.add(record.get("id"))

    # create diff
    to_insert = new_ids - existing_ids
    to_delete = existing_ids - new_ids
    unchanged = new_ids & existing_ids

    # create log
    logger.info(
            "DVD sync diff | "
            f"insert: {len(to_insert)}, "
            f"delete: {len(to_delete)}, "
            f"unchanged: {len(unchanged)}"
        )
    
    return to_insert, to_delete

def sync_dvd_format(engine, data, to_insert, to_delete):
    # 3. Update dvd_format table
    #   a. If record is not in dvd_format, add it
    #   b. If record in dvd_format is not in API, delete it

    logger.info("Starting sync...")

    with engine.connect() as conn:
        if to_insert:
            for dvd in data:
                if dvd['id'] in to_insert:
                    conn.execute(
                        insert(dvd_format),
                        dvd
                    )

        if to_delete:
            conn.execute(
                delete(dvd_format).where(dvd_format.c.id.in_(to_delete))
            )
        
        conn.commit()
    
    logger.info("Sync completed.")

def update_dvd_format():
    # running all functions for updating dvd_format
    engine = connect_with_connector()
    data = fetch_dvd_data()
    to_insert, to_delete = generate_dif_d(engine, data)
    sync_dvd_format(engine, data, to_insert, to_delete)

### End section ###

### Functions for updating dvd_editions table ###

def generate_dif_e(engine):
    # 1. Create diff
    logger.info("Generating dif...")
    # get ids in editions and ids in dvd_format
    with engine.connect() as conn:
        dvd_format_ids = set()
        stmt = select(dvd_format.c.editionId)
        for row in conn.execute(stmt):
            dvd_format_ids.add(row[0])
        
        dvd_editions_ids = set()
        stmt = select(dvd_editions.c.id)
        for row in conn.execute(stmt):
            dvd_editions_ids.add(row[0])

        # create diff
        to_insert = dvd_format_ids - dvd_editions_ids
        to_delete = dvd_editions_ids - dvd_format_ids
        unchanged = dvd_editions_ids & dvd_format_ids

        # create log
        logger.info(
                "DVD sync diff | "
                f"insert: {len(to_insert)}, "
                f"delete: {len(to_delete)}, "
                f"unchanged: {len(unchanged)}"
            )
        return to_insert, to_delete

async def gather_dvd_editions(to_insert):
    # 2. gather dvd editions
    logger.info("Inserting editions...")

    if not to_insert:
        logger.info("Aborting: nothing to insert")
        return
    
    rate_limiter = Limiter(5/1)
    coroutines = [get_edition(rate_limiter, id) for id in to_insert]

    editions = await asyncio.gather(*coroutines)
    return editions

def insert_dvd_editions(engine, editions):
    # 3. insert dvd editions into db
    with engine.connect() as conn:
        conn.execute(
            insert(dvd_editions),
            editions
        )

        conn.commit()

def delete_dvd_editions(engine, to_delete):
    # 4. delete dvd editions
    logger.info("Deleting editions...")

    with engine.connect() as conn:
        conn.execute(
            delete(dvd_editions).where(dvd_editions.c.id.in_(to_delete))
        )
        
        conn.commit()

def update_dvd_editions():
    # putting it all together
    logger.info("Updating dvd_editions...")
    engine = connect_with_connector()
    to_insert, to_delete = generate_dif_e(engine)
    editions = asyncio.run(gather_dvd_editions(to_insert))
    insert_dvd_editions(engine, editions)
    delete_dvd_editions(engine, to_delete)

### End section ###

if __name__ == "__main__":
    update_dvd_format()
    update_dvd_editions()