from sqlite3 import OperationalError

from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

# Replace with your actual DB details
DB_SERVER = "DESKTOP-PLFK2B5\\SQLEXPRESS"
DB_NAME = "EINV-TESTDB-LIVE-HUST"
DB_USER = "sa"
DB_PASSWORD = "Ea@12345"

# ODBC connection string (you must have ODBC driver installed, e.g., ODBC Driver 17 for SQL Server)
connection_string = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER},1433/{DB_NAME}"
    "?driver=ODBC+Driver+17+for+SQL+Server&Trusted_Connection=no&MARS_Connection=Yes"
)

# Create engine with connection pooling
engine = create_engine(
    connection_string,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800
)

# Test a query
def test_query():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT TOP 5 name FROM ORDR"))
            for row in result:
                print(row)
    except OperationalError as e:
        print(f"Database connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_query()

