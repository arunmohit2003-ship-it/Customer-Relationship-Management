"""
dao/customer_dao.py
--------------------
All SQL for the `customers` table lives here, and nowhere else.
Every method opens its own cursor, runs ONE parameterized query
(never string-formatted SQL, to prevent injection), and returns
plain Customer objects to the controller layer.
"""

from mysql.connector import Error
from dao.db_connection import DatabaseConnection
from models.customer import Customer


class CustomerDAO:

    @staticmethod
    def _row_to_customer(row):
        return Customer(
            customer_id=row["customer_id"],
            full_name=row["full_name"],
            company_name=row["company_name"],
            email=row["email"],
            phone=row["phone"],
            address=row["address"],
            city=row["city"],
            state=row["state"],
            customer_type=row["customer_type"],
            source=row["source"],
            assigned_to=row["assigned_to"],
            notes=row["notes"],
            created_date=row["created_date"],
        )

    @staticmethod
    def create(customer: Customer) -> int:
        query = """
            INSERT INTO customers
                (full_name, company_name, email, phone, address, city, state,
                 customer_type, source, assigned_to, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (customer.full_name, customer.company_name, customer.email,
                  customer.phone, customer.address, customer.city, customer.state,
                  customer.customer_type, customer.source, customer.assigned_to,
                  customer.notes)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.lastrowid
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to add customer: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_all(search_term: str = "", customer_type: str = "All"):
        query = "SELECT * FROM customers WHERE 1=1"
        params = []
        if search_term:
            query += " AND (full_name LIKE %s OR company_name LIKE %s OR phone LIKE %s OR email LIKE %s)"
            like = f"%{search_term}%"
            params.extend([like, like, like, like])
        if customer_type and customer_type != "All":
            query += " AND customer_type = %s"
            params.append(customer_type)
        query += " ORDER BY customer_id DESC"

        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [CustomerDAO._row_to_customer(r) for r in rows]
        except Error as err:
            raise RuntimeError(f"Failed to fetch customers: {err}")
        finally:
            cursor.close()

    @staticmethod
    def get_by_id(customer_id: int):
        query = "SELECT * FROM customers WHERE customer_id = %s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute(query, (customer_id,))
            row = cursor.fetchone()
            return CustomerDAO._row_to_customer(row) if row else None
        except Error as err:
            raise RuntimeError(f"Failed to fetch customer: {err}")
        finally:
            cursor.close()

    @staticmethod
    def update(customer: Customer) -> bool:
        query = """
            UPDATE customers
               SET full_name=%s, company_name=%s, email=%s, phone=%s, address=%s,
                   city=%s, state=%s, customer_type=%s, source=%s, assigned_to=%s, notes=%s
             WHERE customer_id=%s
        """
        params = (customer.full_name, customer.company_name, customer.email,
                  customer.phone, customer.address, customer.city, customer.state,
                  customer.customer_type, customer.source, customer.assigned_to,
                  customer.notes, customer.customer_id)
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to update customer: {err}")
        finally:
            cursor.close()

    @staticmethod
    def delete(customer_id: int) -> bool:
        query = "DELETE FROM customers WHERE customer_id = %s"
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(query, (customer_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Error as err:
            conn.rollback()
            raise RuntimeError(f"Failed to delete customer: {err}")
        finally:
            cursor.close()

    @staticmethod
    def count_all():
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM customers")
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def count_by_type(customer_type: str):
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM customers WHERE customer_type=%s", (customer_type,))
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    @staticmethod
    def get_all_names():
        """Returns [(customer_id, full_name), ...] for populating dropdowns."""
        conn = DatabaseConnection.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT customer_id, full_name FROM customers ORDER BY full_name")
            return cursor.fetchall()
        finally:
            cursor.close()
