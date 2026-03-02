# fetchitems
## Project Goals
This project aims to maintain a SQL database which is a real-time representation of items available at a public library. The database will be used in future projects.

### Creating the Database
The database has been created using MySQL and is hosted by Google Cloud SQL.

### Keeping the Database Updated
The program will:
- Retrieve items that are currently available at the library using the library catalog (Vega API)
- Add items to database that available and not already in the database
- Remove items from the database that are not currently available
- Periodically run the script using GitHub actions to keep database updated

## Tech Stack
- <b>SQL Alchemy</b> for interacting with the database
- <b>Cloud SQL Python Connector</b> for connecting to Google Cloud SQL database
- <b>Google Cloud SQL</b> for hosting the database
- <b>MySQL</b> for database management system
