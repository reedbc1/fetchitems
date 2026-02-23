import os
from google.cloud.sql.connector import Connector
import sqlalchemy
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print(os.getenv("INSTANCE_CONNECTION_NAME"))

# initialize Connector object
connector = Connector()

# initialize SQLAlchemy connection pool with Connector
pool = sqlalchemy.create_engine(
    "mysql+pymysql://",
    creator=lambda: connector.connect(
        os.getenv("INSTANCE_CONNECTION_NAME"),
        "pymysql",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        db=os.getenv("DB_NAME")
    ),
)

with pool.connect() as db_conn:
   # query database
    result = db_conn.execute(sqlalchemy.text("SELECT * from ratings")).fetchall()

    # commit transaction (SQLAlchemy v2.X.X is commit as you go)
    db_conn.commit()

    # Do something with the results
    for row in result:
        print(row)

connector.close()