"""
models/customer.py
-------------------
Plain data object representing one row of the `customers` table.
Models never talk to the database directly - that is the DAO's job.
"""


class Customer:
    def __init__(self, customer_id=None, full_name="", company_name="", email="",
                 phone="", address="", city="", state="", customer_type="Lead",
                 source="Other", assigned_to="", notes="", created_date=None):
        self.customer_id = customer_id
        self.full_name = full_name
        self.company_name = company_name
        self.email = email
        self.phone = phone
        self.address = address
        self.city = city
        self.state = state
        self.customer_type = customer_type
        self.source = source
        self.assigned_to = assigned_to
        self.notes = notes
        self.created_date = created_date

    def __repr__(self):
        return f"<Customer {self.customer_id}: {self.full_name}>"
