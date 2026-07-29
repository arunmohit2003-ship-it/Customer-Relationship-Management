"""
dao/user_dao.py
----------------
Handles login authentication against the `users` table.
Passwords are never stored or compared in plain text - only their
SHA-256 hash is ever written to, or read from, the database.
"""

import hashlib
from mysql.connector import Error
from dao.db_connection import DatabaseConnection


class UserDAO:

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    @staticmethod
    def verify_login(username: str, password: str):
        """Returns a dict with user info if the credentials are valid, else None."""
        query = "SELECT user_id, username, full_name, role, password_hash FROM users WHERE username=%s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (username,))
            row = cursor.fetchone()
            if row and row["password_hash"] == UserDAO._hash(password):
                return {
                    "user_id": row["user_id"],
                    "username": row["username"],
                    "full_name": row["full_name"],
                    "role": row["role"],
                }
            return None
        except Error as err:
            raise RuntimeError(f"Login check failed: {err}")
        finally:
            cursor.close()
