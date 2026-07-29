"""
models/contact_history.py
--------------------------
Plain data object representing one row of the `contact_history` table.
`customer_name` is populated via a JOIN in ContactHistoryDAO for display.
"""


class ContactHistory:
    def __init__(self, history_id=None, customer_id=None, contact_date=None,
                 contact_time=None, contact_type="Call", subject="", description="",
                 outcome="Neutral", handled_by="", created_date=None, customer_name=""):
        self.history_id = history_id
        self.customer_id = customer_id
        self.contact_date = contact_date
        self.contact_time = contact_time
        self.contact_type = contact_type
        self.subject = subject
        self.description = description
        self.outcome = outcome
        self.handled_by = handled_by
        self.created_date = created_date
        self.customer_name = customer_name

    def __repr__(self):
        return f"<ContactHistory {self.history_id}: {self.subject}>"
