"""
controllers/followup_controller.py
------------------------------------
Sits between the views and FollowUpDAO. Validates everything coming
from the UI before it reaches the database.
"""

from dao.followup_dao import FollowUpDAO
from models.followup import FollowUp


class FollowUpController:

    @staticmethod
    def _validate(customer_id, followup_date, purpose):
        if not customer_id:
            raise ValueError("Please select a customer.")
        if not followup_date:
            raise ValueError("Follow-up date is required.")
        if not purpose or not purpose.strip():
            raise ValueError("Purpose is required.")

    @staticmethod
    def schedule_followup(customer_id, followup_date, followup_time, purpose,
                           priority, status, remarks):
        FollowUpController._validate(customer_id, followup_date, purpose)
        f = FollowUp(
            customer_id=customer_id, followup_date=followup_date,
            followup_time=followup_time or None, purpose=purpose.strip(),
            priority=priority, status=status, remarks=remarks.strip()
        )
        return FollowUpDAO.create(f)

    @staticmethod
    def update_followup(followup_id, customer_id, followup_date, followup_time,
                         purpose, priority, status, remarks):
        FollowUpController._validate(customer_id, followup_date, purpose)
        f = FollowUp(
            followup_id=followup_id, customer_id=customer_id, followup_date=followup_date,
            followup_time=followup_time or None, purpose=purpose.strip(),
            priority=priority, status=status, remarks=remarks.strip()
        )
        return FollowUpDAO.update(f)

    @staticmethod
    def mark_status(followup_id, status):
        return FollowUpDAO.update_status(followup_id, status)

    @staticmethod
    def delete_followup(followup_id):
        return FollowUpDAO.delete(followup_id)

    @staticmethod
    def get_all_followups(status="All", search_term=""):
        return FollowUpDAO.get_all(status, search_term)

    @staticmethod
    def get_followups_for_customer(customer_id):
        return FollowUpDAO.get_by_customer(customer_id)

    @staticmethod
    def get_followup(followup_id):
        return FollowUpDAO.get_by_id(followup_id)

    @staticmethod
    def get_dashboard_counts():
        return {
            "pending": FollowUpDAO.count_pending(),
            "today": FollowUpDAO.count_today(),
            "overdue": FollowUpDAO.count_overdue(),
        }

    @staticmethod
    def get_upcoming(limit=5):
        return FollowUpDAO.get_upcoming(limit)
