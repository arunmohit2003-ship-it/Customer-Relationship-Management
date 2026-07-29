"""
verify_setup.py
-----------------
Optional setup-verification script. Run this AFTER importing
database/schema.sql and updating config.py, and BEFORE opening the
GUI, to confirm your MySQL connection and every Customer / Follow-up
/ Contact History operation works correctly on your machine:

    python verify_setup.py

It creates a few temporary test records, exercises every add / view /
update / delete operation against your real database, then cleans up
after itself. Nothing it does is destructive to your existing data.
If every line prints [PASS], the application is ready to run.
"""

import sys
import traceback
from datetime import date, time, timedelta

results = {"pass": 0, "fail": 0}


def check(name, fn):
    try:
        fn()
        print(f"  [PASS] {name}")
        results["pass"] += 1
    except Exception as e:
        print(f"  [FAIL] {name} -> {type(e).__name__}: {e}")
        traceback.print_exc()
        results["fail"] += 1


print("=== 1. Imports ===")
def t_imports():
    from dao.db_connection import DatabaseConnection
    from dao.customer_dao import CustomerDAO
    from dao.followup_dao import FollowUpDAO
    from dao.contact_history_dao import ContactHistoryDAO
    from dao.user_dao import UserDAO
    from controllers.customer_controller import CustomerController
    from controllers.followup_controller import FollowUpController
    from controllers.contact_history_controller import ContactHistoryController
    from controllers.auth_controller import AuthController
    from models.customer import Customer
    from models.followup import FollowUp
    from models.contact_history import ContactHistory
check("import every dao/controller/model module", t_imports)

from controllers.customer_controller import CustomerController
from controllers.followup_controller import FollowUpController
from controllers.contact_history_controller import ContactHistoryController
from controllers.auth_controller import AuthController

print("\n=== 2. Auth ===")
def t_login_ok():
    user = AuthController.login("admin", "admin123")
    assert user["username"] == "admin", "username mismatch"
check("correct login succeeds", t_login_ok)

def t_login_bad_password():
    try:
        AuthController.login("admin", "wrongpassword")
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass
check("wrong password is rejected", t_login_bad_password)

def t_login_bad_user():
    try:
        AuthController.login("no_such_user", "whatever")
        raise AssertionError("should have raised ValueError")
    except ValueError:
        pass
check("unknown username is rejected", t_login_bad_user)

print("\n=== 3. Customer CRUD ===")
new_customer_id = {}

def t_customer_validation_bad_phone():
    try:
        CustomerController.add_customer("Test User", "TestCo", "test@test.com",
                                         "12345", "Addr", "City", "State", "Lead",
                                         "Other", "Aayush", "")
        raise AssertionError("should have rejected bad phone")
    except ValueError:
        pass
check("customer add rejects invalid phone", t_customer_validation_bad_phone)

def t_customer_validation_bad_email():
    try:
        CustomerController.add_customer("Test User", "TestCo", "not-an-email",
                                         "9812345670", "Addr", "City", "State", "Lead",
                                         "Other", "Aayush", "")
        raise AssertionError("should have rejected bad email")
    except ValueError:
        pass
check("customer add rejects invalid email", t_customer_validation_bad_email)

def t_customer_create():
    cid = CustomerController.add_customer(
        "Smoke Test Customer", "Smoke Test Co", "smoke@test.com", "9812345670",
        "1 Test Street", "Rewari", "Haryana", "Lead", "Website", "Aayush",
        "Created by automated smoke test")
    assert cid and cid > 0
    new_customer_id["id"] = cid
check("create customer", t_customer_create)

def t_customer_read():
    c = CustomerController.get_customer(new_customer_id["id"])
    assert c is not None
    assert c.full_name == "Smoke Test Customer"
    assert c.phone == "9812345670"
check("read customer by id", t_customer_read)

def t_customer_list_and_search():
    all_customers = CustomerController.get_all_customers()
    assert len(all_customers) >= 6, f"expected >=6 customers, got {len(all_customers)}"
    found = CustomerController.get_all_customers(search_term="Smoke Test")
    assert len(found) == 1
    filtered = CustomerController.get_all_customers(customer_type="Lead")
    assert all(c.customer_type == "Lead" for c in filtered)
check("list all + search + filter by type", t_customer_list_and_search)

def t_customer_update():
    ok = CustomerController.update_customer(
        new_customer_id["id"], "Smoke Test Customer Updated", "Smoke Test Co",
        "smoke@test.com", "9812345670", "1 Test Street", "Rewari", "Haryana",
        "Prospect", "Website", "Aayush", "Updated by smoke test")
    assert ok
    c = CustomerController.get_customer(new_customer_id["id"])
    assert c.full_name == "Smoke Test Customer Updated"
    assert c.customer_type == "Prospect"
check("update customer", t_customer_update)

def t_customer_dashboard_counts():
    counts = CustomerController.get_dashboard_counts()
    assert "total" in counts and counts["total"] >= 6
check("dashboard counts for customers", t_customer_dashboard_counts)

def t_customer_names_dropdown():
    names = CustomerController.get_customer_names()
    assert len(names) >= 6
    assert all(isinstance(n[0], int) for n in names)
check("get_customer_names for dropdown", t_customer_names_dropdown)

print("\n=== 4. Follow-up CRUD (depends on customer above) ===")
new_followup_id = {}

def t_followup_validation():
    try:
        FollowUpController.schedule_followup(None, date.today(), time(10, 0),
                                              "Test", "Medium", "Pending", "")
        raise AssertionError("should reject missing customer")
    except ValueError:
        pass
check("follow-up rejects missing customer", t_followup_validation)

def t_followup_create():
    fid = FollowUpController.schedule_followup(
        new_customer_id["id"], date.today() + timedelta(days=1), time(14, 30),
        "Smoke Test Follow-up", "High", "Pending", "Automated test remark")
    assert fid and fid > 0
    new_followup_id["id"] = fid
check("create follow-up (schedule)", t_followup_create)

def t_followup_read():
    f = FollowUpController.get_followup(new_followup_id["id"])
    assert f is not None
    assert f.purpose == "Smoke Test Follow-up"
    assert f.customer_name == "Smoke Test Customer Updated"
check("read follow-up by id (joined with customer name)", t_followup_read)

def t_followup_list_filter():
    all_f = FollowUpController.get_all_followups()
    assert len(all_f) >= 7
    pending = FollowUpController.get_all_followups(status="Pending")
    assert all(f.status == "Pending" for f in pending)
    searched = FollowUpController.get_all_followups(search_term="Smoke Test")
    assert len(searched) == 1
check("list all + filter by status + search", t_followup_list_filter)

def t_followup_for_customer():
    fs = FollowUpController.get_followups_for_customer(new_customer_id["id"])
    assert len(fs) == 1
check("get follow-ups for a specific customer", t_followup_for_customer)

def t_followup_update():
    ok = FollowUpController.update_followup(
        new_followup_id["id"], new_customer_id["id"], date.today() + timedelta(days=2),
        time(9, 0), "Smoke Test Follow-up Updated", "Low", "Rescheduled", "Updated remark")
    assert ok
    f = FollowUpController.get_followup(new_followup_id["id"])
    assert f.status == "Rescheduled"
    assert f.priority == "Low"
check("update follow-up", t_followup_update)

def t_followup_mark_status():
    ok = FollowUpController.mark_status(new_followup_id["id"], "Completed")
    assert ok
    f = FollowUpController.get_followup(new_followup_id["id"])
    assert f.status == "Completed"
check("mark follow-up status (quick action)", t_followup_mark_status)

def t_followup_dashboard_counts():
    counts = FollowUpController.get_dashboard_counts()
    assert set(counts.keys()) == {"pending", "today", "overdue"}
check("dashboard counts for follow-ups", t_followup_dashboard_counts)

def t_followup_upcoming_limit():
    # This specifically tests that "LIMIT %s" parameter binding works
    # correctly with mysql-connector-python (a common gotcha).
    upcoming = FollowUpController.get_upcoming(3)
    assert len(upcoming) <= 3
check("get_upcoming() - tests LIMIT %s parameter binding", t_followup_upcoming_limit)

print("\n=== 5. Contact History CRUD (depends on customer above) ===")
new_history_id = {}

def t_contact_validation():
    try:
        ContactHistoryController.log_contact(None, date.today(), time(10, 0),
                                              "Call", "Test", "", "Neutral", "Aayush")
        raise AssertionError("should reject missing customer")
    except ValueError:
        pass
check("contact log rejects missing customer", t_contact_validation)

def t_contact_create():
    hid = ContactHistoryController.log_contact(
        new_customer_id["id"], date.today(), time(11, 15), "Call",
        "Smoke Test Contact", "Automated test description", "Positive", "Aayush")
    assert hid and hid > 0
    new_history_id["id"] = hid
check("create contact history entry", t_contact_create)

def t_contact_read():
    h = ContactHistoryController.get_contact(new_history_id["id"])
    assert h is not None
    assert h.subject == "Smoke Test Contact"
    assert h.customer_name == "Smoke Test Customer Updated"
check("read contact by id (joined with customer name)", t_contact_read)

def t_contact_list_filter():
    all_h = ContactHistoryController.get_all_contacts()
    assert len(all_h) >= 6
    calls = ContactHistoryController.get_all_contacts(contact_type="Call")
    assert all(h.contact_type == "Call" for h in calls)
    searched = ContactHistoryController.get_all_contacts(search_term="Smoke Test")
    assert len(searched) == 1
check("list all + filter by type + search", t_contact_list_filter)

def t_contact_for_customer():
    hs = ContactHistoryController.get_contacts_for_customer(new_customer_id["id"])
    assert len(hs) == 1
check("get contact history for a specific customer", t_contact_for_customer)

def t_contact_update():
    ok = ContactHistoryController.update_contact(
        new_history_id["id"], new_customer_id["id"], date.today(), time(11, 15),
        "Email", "Smoke Test Contact Updated", "Updated description",
        "Negative", "Aayush")
    assert ok
    h = ContactHistoryController.get_contact(new_history_id["id"])
    assert h.contact_type == "Email"
    assert h.outcome == "Negative"
check("update contact history entry", t_contact_update)

def t_contact_recent_limit():
    # Also tests "LIMIT %s" parameter binding.
    recent = ContactHistoryController.get_recent(3)
    assert len(recent) <= 3
check("get_recent() - tests LIMIT %s parameter binding", t_contact_recent_limit)

def t_contact_total_count():
    total = ContactHistoryController.get_total_count()
    assert total >= 6
check("total contact history count", t_contact_total_count)

print("\n=== 6. Cleanup (delete test records) ===")
def t_delete_followup():
    ok = FollowUpController.delete_followup(new_followup_id["id"])
    assert ok
    assert FollowUpController.get_followup(new_followup_id["id"]) is None
check("delete follow-up", t_delete_followup)

def t_delete_contact():
    ok = ContactHistoryController.delete_contact(new_history_id["id"])
    assert ok
    assert ContactHistoryController.get_contact(new_history_id["id"]) is None
check("delete contact history entry", t_delete_contact)

def t_delete_customer_cascade():
    # Add a follow-up + contact, then delete the customer, and verify
    # the ON DELETE CASCADE foreign keys clean up automatically.
    fid = FollowUpController.schedule_followup(
        new_customer_id["id"], date.today(), time(10, 0), "Cascade test", "Low",
        "Pending", "")
    hid = ContactHistoryController.log_contact(
        new_customer_id["id"], date.today(), time(10, 0), "Call", "Cascade test",
        "", "Neutral", "Aayush")
    ok = CustomerController.delete_customer(new_customer_id["id"])
    assert ok
    assert CustomerController.get_customer(new_customer_id["id"]) is None
    assert FollowUpController.get_followup(fid) is None, "ON DELETE CASCADE did not clean up follow_ups"
    assert ContactHistoryController.get_contact(hid) is None, "ON DELETE CASCADE did not clean up contact_history"
check("delete customer cascades to follow_ups + contact_history", t_delete_customer_cascade)

print("\n" + "=" * 60)
print(f"RESULTS: {results['pass']} passed, {results['fail']} failed")
print("=" * 60)
sys.exit(1 if results["fail"] else 0)
