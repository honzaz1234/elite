from sqlalchemy import create_engine, MetaData, Table, text

TABLE_NAME = "teams"
COLUMN = "uid"
# Connect to the database
db_url = "sqlite:///./database/hockey_v9.db"
engine = create_engine(db_url)
metadata = MetaData()
metadata.reflect(bind=engine)

# Open connection
with engine.connect() as connection:
    # Iterate over all tables
    for table in metadata.tables.values():
        for fk in table.foreign_keys:
            if fk.column.table.name == TABLE_NAME:  # Check if referencing teams
                fk_column = fk.parent.name  # Column name in the referencing table
                table_name = table.name  # Referencing table name

                print(f"Updating {table_name}.{fk_column} where {TABLE_NAME}.{COLUMN} is NULL")

                # Execute update query
                query = text(f"""
                    UPDATE {table_name}
                    SET {fk_column} = NULL
                    WHERE {fk_column} IN (SELECT id FROM {TABLE_NAME} WHERE {COLUMN} IS NULL);
                """)
                connection.execute(query)

    query = text(f"""
                    delete from {TABLE_NAME}
                    where {COLUMN} is NULL
                """)
    connection.execute(query)
    # Commit changes
    connection.commit()

print(f"All foreign key references to {TABLE_NAME} where {COLUMN} is NULL have been updated and null value from {TABLE_NAME} was deleted.")
