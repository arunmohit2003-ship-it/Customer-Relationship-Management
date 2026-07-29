"""
controllers/contact_history_controller.py
--------------------------------------------
Sits between the views and ContactHistoryDAO. Validates everything
coming from the UI before it reaches the database.
"""

from dao.contact_history_dao import ContactHistoryDAO
from models.contact_history import ContactHistory


class ContactHistoryController:

    @staticmethod
    def _validate(customer_id, contact_date, subject):
        if not customer_id:
            raise ValueError("Please select a customer.")
        if not contact_date:
            raise ValueError("Contact date is required.")
        if not subject or not subject.strip():
            raise ValueError("Subject is required.")

    @staticmethod
    def log_contact(customer_id, contact_date, contact_time, contact_type, subject,
                     description, outcome, handled_by):
        ContactHistoryController._validate(customer_id, contact_date, subject)
        h = ContactHistory(
            customer_id=customer_id, contact_date=contact_date,
            contact_time=contact_time or None, contact_type=contact_type,
            subject=subject.strip(), description=description.strip(),
            outcome=outcome, handled_by=handled_by.strip()
        )
        return ContactHistoryDAO.create(h)

    @staticmethod
    def update_contact(history_id, customer_id, contact_date, contact_time,
                        contact_type, subject, description, outcome, handled_by):
        ContactHistoryController._validate(customer_id, contact_date, subject)
        h = ContactHistory(
            history_id=history_id, customer_id=customer_id, contact_date=contact_date,
            contact_time=contact_time or None, contact_type=contact_type,
            subject=subject.strip(), description=description.strip(),
            outcome=outcome, handled_by=handled_by.strip()
        )
        return ContactHistoryDAO.update(h)

    @staticmethod
    def delete_contact(history_id):
        return ContactHistoryDAO.delete(history_id)

    @staticmethod
    def get_all_contacts(contact_type="All", search_term=""):
        return ContactHistoryDAO.get_all(contact_type, search_term)

    @staticmethod
    def get_contacts_for_customer(customer_id):
        return ContactHistoryDAO.get_by_customer(customer_id)

    @staticmethod
    def get_contact(history_id):
        return ContactHistoryDAO.get_by_id(history_id)

    @staticmethod
    def get_recent(limit=5):
        return ContactHistoryDAO.get_recent(limit)

    @staticmethod
    def get_total_count():
        return ContactHistoryDAO.count_all()
