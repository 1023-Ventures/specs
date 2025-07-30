import os
from typing import Union
from .database import Database
from .postgres_database import PostgreSQLDatabase

def get_database() -> Union[Database, PostgreSQLDatabase]:
    """Factory function to get the appropriate database instance"""
    db_type = os.getenv("DATABASE_TYPE", "postgresql").lower()
    
    if db_type == "postgresql" or db_type == "postgres":
        connection_string = os.getenv(
            "DATABASE_URL",
            "host=localhost port=5432 dbname=specs_auth user=specs_user password=specs_password"
        )
        return PostgreSQLDatabase(connection_string)
    else:
        # Default to SQLite
        db_path = os.getenv("DATABASE_PATH", "auth.db")
        return Database(db_path)
