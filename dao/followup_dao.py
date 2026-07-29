"""
dao/followup_dao.py
--------------------
All SQL for the `follow_ups` table. Every SELECT joins against
`customers` so the UI always has the customer's name available
without a second round trip.
"""

from mysql.connector import Error
from dao.db_connection import DatabaseConnection
from models.followup import FollowUp


class FollowUpDAO:

    @staticmethod
    def _row_to_followup(row):
        return FollowUp(
            followup_id=row["followup_id"],
            customer_id=row["customer_id"],
            followup_date=row["followup_date"],
            followup_time=row["followup_time"],
            purpose=row["purpose"],
            priority=row["priority"],
            status=row["status"],
            remarks=row["remarks"],
            created_date=row["created_date"],
            customer_name=row.get("full_name", ""),
        )

    @staticmethod
    def create(f: FollowUp) -> int:
        query = """
            INSERT INTO follow_ups
                (customer_id, followup_date, followup_time, purpose, priority, status, remarks)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params = (f.customer_id, f.followup_date, f.followup_time, f.purpose,
                  f.priority, f.status, f.remarks)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to schedule follow-up: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_all(status: str = "All", search_term: str = ""):
        query = """
            SELECT f.*, c.full_name
              FROM follow_ups f
              JOIN customers c ON f.customer_id = c.customer_id
             WHERE 1=1
        """
        params = []
        if status and status != "All":
            query += " AND f.status = %s"
            params.append(status)
        if search_term:
            query += " AND (c.full_name LIKE %s OR f.purpose LIKE %s)"
            like = f"%{search_term}%"
            params.extend([like, like])
        query += " ORDER BY f.followup_date ASC, f.followup_time ASC"

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [FollowUpDAO._row_to_followup(r) for r in rows]
        except Error as err:
            raise RuntimeError(f"Failed to fetch follow-ups: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_by_customer(customer_id: int):
        query = """
            SELECT f.*, c.full_name
              FROM follow_ups f
              JOIN customers c ON f.customer_id = c.customer_id
             WHERE f.customer_id = %s
             ORDER BY f.followup_date DESC
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (customer_id,))
            rows = cursor.fetchall()
            return [FollowUpDAO._row_to_followup(r) for r in rows]
        except Error as err:
            raise RuntimeError(f"Failed to fetch follow-ups: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(followup_id: int):
        query = """
            SELECT f.*, c.full_name
              FROM follow_ups f
              JOIN customers c ON f.customer_id = c.customer_id
             WHERE f.followup_id = %s
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (followup_id,))
            row = cursor.fetchone()
            return FollowUpDAO._row_to_followup(row) if row else None
        except Error as err:
            raise RuntimeError(f"Failed to fetch follow-up: {err}")
        finally:
            cursor.close()

    @staticmethod
    def update(f: FollowUp) -> bool:
        query = """
            UPDATE follow_ups
               SET customer_id=%s, followup_date=%s, followup_time=%s, purpose=%s,
                   priority=%s, status=%s, remarks=%s
             WHERE followup_id=%s
        """
        params = (f.customer_id, f.followup_date, f.followup_time, f.purpose,
                  f.priority, f.status, f.remarks, f.followup_id)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to update follow-up: {err}")
        finally:
            cursor.close()

    @staticmethod
    def update_status(followup_id: int, status: str) -> bool:
        query = "UPDATE follow_ups SET status=%s WHERE followup_id=%s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (status, followup_id))
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to update status: {err}")
        finally:
            cursor.close()

    @staticmethod
    def delete(followup_id: int) -> bool:
        query = "DELETE FROM follow_ups WHERE followup_id=%s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (followup_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to delete follow-up: {err}")
        finally:
            cursor.close()

    @staticmethod
    def count_pending():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM follow_ups WHERE status='Pending'")
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def count_today():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM follow_ups WHERE followup_date = CURDATE() AND status='Pending'"
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def count_overdue():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM follow_ups WHERE followup_date < CURDATE() AND status='Pending'"
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def get_upcoming(limit: int = 5):
        query = """
            SELECT f.*, c.full_name
              FROM follow_ups f
              JOIN customers c ON f.customer_id = c.customer_id
             WHERE f.status = 'Pending'
             ORDER BY f.followup_date ASC, f.followup_time ASC
             LIMIT %s
        """
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (limit,))
            rows = cursor.fetchall()
            return [FollowUpDAO._row_to_followup(r) for r in rows]
        finally:
            cursor.close()
