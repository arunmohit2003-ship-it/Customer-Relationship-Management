"""
dao/db_connection.py
---------------------
Centralized MySQL connection handler used by every DAO class.
Keeping this in one place means the rest of the app never has to
worry about connection details or re-connecting after a timeout.
"""

import mysql.connector
from mysql.connector import Error
from config import DB_CONFIG


class DatabaseConnection:
    _connection = None

    @classmethod
    def get_connection(cls):
        """Return a live MySQL connection, (re)connecting if needed."""
        try:
            if cls._connection is None or not cls._connection.is_connected():
                cls._connection = mysql.connector.connect(**DB_CONFIG)
            return cls._connection
        except Error as err:
            raise ConnectionError(
                "Could not connect to the MySQL database.\n\n"
                f"Details: {err}\n\n"
                "Please check that:\n"
                "  1. MySQL server is running\n"
                "  2. database/schema.sql has been imported\n"
                "  3. config.py has the correct host / user / password"
            )

    @classmethod
    def close_connection(cls):
        if cls._connection is not None and cls._connection.is_connected():
            cls._connection.close()
            cls._connection = None
