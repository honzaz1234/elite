from hockeydata.database_session import database_session

from sqlalchemy import create_engine, MetaData, Table, text
from sqlalchemy.orm import sessionmaker
import pandas as pd


# Define database URLs
OLD_DB_URL = "sqlite:///./database/hockey_v15_test.db"
NEW_DB_URL = "sqlite:///./database/hockey_v16_test.db"

# Create engines and sessions
old_engine = create_engine(OLD_DB_URL)
new_engine = create_engine(NEW_DB_URL)
OldSession = sessionmaker(bind=old_engine)
NewSession = sessionmaker(bind=new_engine)
old_session = OldSession()
new_session = NewSession()

# Reflect metadata from both databases                                                                                                                     
old_metadata = MetaData()
new_metadata = MetaData()
old_metadata.reflect(bind=old_engine)
new_metadata.reflect(bind=new_engine)

# Find common tables
old_tables = set(old_metadata.tables.keys())
new_tables = set(new_metadata.tables.keys())
common_tables = old_tables.intersection(new_tables)

for table in common_tables:
    new_session.execute(text(f"DELETE FROM {table};"))
new_session.commit()

# Transfer data for common tables
for table_name in common_tables:
    old_table = Table(table_name, old_metadata, autoload_with=old_engine)
    if table_name == 'scrapes':
        continue
    
    new_table = Table(table_name, new_metadata, autoload_with=new_engine)
    # Fetch data from the old table
    query = old_session.query(old_table)
    data = pd.read_sql(
        query.statement, old_engine, parse_dates=['event_time']
        )
    
    if data.empty:
        print(f"Skipping {table_name}: No data found")
        continue

    # Handle additional columns in the new table
    new_columns = set(new_table.columns.keys())
    old_columns = set(old_table.columns.keys())
    matching_columns = list(old_columns.intersection(new_columns))
    
    # Insert only the matching columns
    data = data[matching_columns]  # Drop extra columns
    data.to_sql(table_name, new_engine, if_exists="append", index=False)
    print(f"Transferred {len(data)} records to {table_name}")

# Close sessions
old_session.close()
new_session.close()
