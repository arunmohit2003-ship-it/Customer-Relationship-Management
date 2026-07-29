"""
models/followup.py
-------------------
Plain data object representing one row of the `follow_ups` table.
`customer_name` is not a real column - it is populated via a JOIN
in FollowUpDAO purely for convenient display in the UI.
"""


class FollowUp:
    def __init__(self, followup_id=None, customer_id=None, followup_date=None,
                 followup_time=None, purpose="", priority="Medium", status="Pending",
                 remarks="", created_date=None, customer_name=""):
        self.followup_id = followup_id
        self.customer_id = customer_id
        self.followup_date = followup_date
        self.followup_time = followup_time
        self.purpose = purpose
        self.priority = priority
        self.status = status
        self.remarks = remarks
        self.created_date = created_date
        self.customer_name = customer_name

    def __repr__(self):
        return f"<FollowUp {self.followup_id}: {self.purpose} ({self.status})>"
