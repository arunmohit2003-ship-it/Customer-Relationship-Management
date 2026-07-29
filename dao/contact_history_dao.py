"""
dao/contact_history_dao.py
---------------------------
All SQL for the `contact_history` table. Every SELECT joins against
`customers` so the UI always has the customer's name available.
"""

from mysql.connector import Error
from dao.db_connection import DatabaseConnection
from models.contact_history import ContactHistory


class ContactHistoryDAO:

    @staticmethod
    def _row_to_history(row):
        return ContactHistory(
            history_id=row["history_id"],
            customer_id=row["customer_id"],
            contact_date=row["contact_date"],
            contact_time=row["contact_time"],
            contact_type=row["contact_type"],
            subject=row["subject"],
            description=row["description"],
            outcome=row["outcome"],
            handled_by=row["handled_by"],
            created_date=row["created_date"],
            customer_name=row.get("full_name", ""),
        )

    @staticmethod
    def create(h: ContactHistory) -> int:
        query = """
            INSERT INTO contact_history
                (customer_id, contact_date, contact_time, contact_type, subject,
                 description, outcome, handled_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (h.customer_id, h.contact_date, h.contact_time, h.contact_type,
                  h.subject, h.description, h.outcome, h.handled_by)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to log contact: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_all(contact_type: str = "All", search_term: str = ""):
        query = """
            SELECT h.*, c.full_name
              FROM contact_history h
              JOIN customers c ON h.customer_id = c.customer_id
             WHERE 1=1
        """
        params = []
        if contact_type and contact_type != "All":
            query += " AND h.contact_type = %s"
            params.append(contact_type)
        if search_term:
            query += " AND (c.full_name LIKE %s OR h.subject LIKE %s)"
            like = f"%{search_term}%"
            params.extend([like, like])
        query += " ORDER BY h.contact_date DESC, h.contact_time DESC"

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [ContactHistoryDAO._row_to_history(r) for r in rows]
        except Error as err:
            raise RuntimeError(f"Failed to fetch contact history: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_by_customer(customer_id: int):
        query = """
            SELECT h.*, c.full_name
              FROM contact_history h
              JOIN customers c ON h.customer_id = c.customer_id
             WHERE h.customer_id = %s
             ORDER BY h.contact_date DESC, h.contact_time DESC
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (customer_id,))
            rows = cursor.fetchall()
            return [ContactHistoryDAO._row_to_history(r) for r in rows]
        except Error as err:
            raise RuntimeError(f"Failed to fetch contact history: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(history_id: int):
        query = """
            SELECT h.*, c.full_name
              FROM contact_history h
              JOIN customers c ON h.customer_id = c.customer_id
             WHERE h.history_id = %s
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (history_id,))
            row = cursor.fetchone()
            return ContactHistoryDAO._row_to_history(row) if row else None
        except Error as err:
            raise RuntimeError(f"Failed to fetch contact record: {err}")
        finally:
            cursor.close()

    @staticmethod
    def update(h: ContactHistory) -> bool:
        query = """
            UPDATE contact_history
               SET customer_id=%s, contact_date=%s, contact_time=%s, contact_type=%s,
                   subject=%s, description=%s, outcome=%s, handled_by=%s
             WHERE history_id=%s
        """
        params = (h.customer_id, h.contact_date, h.contact_time, h.contact_type,
                  h.subject, h.description, h.outcome, h.handled_by, h.history_id)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to update contact log: {err}")
        finally:
            cursor.close()

    @staticmethod
    def delete(history_id: int) -> bool:
        query = "DELETE FROM contact_history WHERE history_id=%s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (history_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to delete contact log: {err}")
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM contact_history")
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def get_recent(limit: int = 5):
        query = """
            SELECT h.*, c.full_name
              FROM contact_history h
              JOIN customers c ON h.customer_id = c.customer_id
             ORDER BY h.contact_date DESC, h.contact_time DESC
             LIMIT %s
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [ContactHistoryDAO._row_to_history(r) for r in rows]
        finally:
            cursor.close()
