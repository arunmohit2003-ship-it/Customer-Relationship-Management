"""
controllers/customer_controller.py
------------------------------------
Sits between the views and CustomerDAO. Validates everything coming
from the UI *before* it ever reaches the database, and raises a
plain ValueError with a friendly message when something is wrong.
"""

import re
from dao.customer_dao import CustomerDAO
from models.customer import Customer

PHONE_PATTERN = re.compile(r"^[6-9]\d{9}$")
EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


class CustomerController:

    @staticmethod
    def _validate(full_name, phone, email):
        if not full_name or not full_name.strip():
            raise ValueError("Full name is required.")
        if not phone or not phone.strip():
            raise ValueError("Phone number is required.")
        if not PHONE_PATTERN.match(phone.strip()):
            raise ValueError("Enter a valid 10-digit Indian mobile number.")
        if email and email.strip() and not EMAIL_PATTERN.match(email.strip()):
            raise ValueError("Enter a valid email address (or leave it blank).")

    @staticmethod
    def add_customer(full_name, company_name, email, phone, address, city, state,
                      customer_type, source, assigned_to, notes):
        CustomerController._validate(full_name, phone, email)
        customer = Customer(
            full_name=full_name.strip(), company_name=company_name.strip(),
            email=email.strip(), phone=phone.strip(), address=address.strip(),
            city=city.strip(), state=state.strip(), customer_type=customer_type,
            source=source, assigned_to=assigned_to.strip(), notes=notes.strip()
        )
        return CustomerDAO.create(customer)

    @staticmethod
    def update_customer(customer_id, full_name, company_name, email, phone, address,
                         city, state, customer_type, source, assigned_to, notes):
        CustomerController._validate(full_name, phone, email)
        customer = Customer(
            customer_id=customer_id, full_name=full_name.strip(),
            company_name=company_name.strip(), email=email.strip(), phone=phone.strip(),
            address=address.strip(), city=city.strip(), state=state.strip(),
            customer_type=customer_type, source=source, assigned_to=assigned_to.strip(),
            notes=notes.strip()
        )
        return CustomerDAO.update(customer)

    @staticmethod
    def delete_customer(customer_id):
        return CustomerDAO.delete(customer_id)

    @staticmethod
    def get_all_customers(search_term="", customer_type="All"):
        return CustomerDAO.get_all(search_term, customer_type)

    @staticmethod
    def get_customer(customer_id):
        return CustomerDAO.get_by_id(customer_id)

    @staticmethod
    def get_dashboard_counts():
        return {
            "total": CustomerDAO.count_all(),
            "active": CustomerDAO.count_by_type("Active"),
            "leads": CustomerDAO.count_by_type("Lead"),
            "prospects": CustomerDAO.count_by_type("Prospect"),
        }

    @staticmethod
    def get_customer_names():
        return CustomerDAO.get_all_names()
