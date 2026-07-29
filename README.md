# CRM Pro — Customer Relationship Management System

A desktop CRM application built with **Python, Tkinter, and MySQL**, using clean
**MVC + DAO architecture**. Built as a portfolio-ready, production-style project.

---

## Features

**Customer Records**
- Add / edit / delete customers with full contact details
- Status tracking: Lead → Prospect → Active → Inactive
- Search by name, company, phone, or email; filter by status
- Export the customer list to CSV

**Follow-up Status**
- Schedule follow-ups against any customer (date, time, purpose, priority)
- Status workflow: Pending → Completed / Cancelled / Rescheduled
- Overdue pending follow-ups are automatically highlighted in the list
- One-click "Mark Completed" / "Cancel Follow-up" actions

**Contact History**
- Log every interaction: Call, Email, Meeting, WhatsApp, SMS, Visit
- Record the outcome (Positive / Negative / Neutral / No Response)
- Full history is searchable and filterable by type

**Ties it together**
- **Customer 360° View** — double-click any customer to see their full profile,
  every scheduled follow-up, and their entire contact history in one screen
- **Dashboard** — live counts (total customers, pending / due-today / overdue
  follow-ups) plus upcoming follow-ups and recent contact activity
- **Login screen** with hashed-password authentication

---

## Tech Stack

| Layer          | Technology                              |
|-----------------|------------------------------------------|
| UI              | Tkinter + ttk (custom theme, no external UI framework) |
| Database        | MySQL 8 (or MariaDB)                     |
| DB Driver       | `mysql-connector-python`                 |
| Date picker     | `tkcalendar`                             |
| Architecture    | MVC + DAO (Model / View / Controller / Data-Access-Object) |

---

## Project Structure

```
CRM_System/
├── main.py                    # Entry point — run this file
├── config.py                  # <-- your MySQL credentials go here
├── requirements.txt
├── verify_setup.py            # optional: verifies your DB setup end-to-end
├── database/
│   └── schema.sql             # creates the DB, tables, and demo data
├── models/                    # plain data classes
│   ├── customer.py
│   ├── followup.py
│   └── contact_history.py
├── dao/                       # all SQL lives here, nowhere else
│   ├── db_connection.py
│   ├── customer_dao.py
│   ├── followup_dao.py
│   ├── contact_history_dao.py
│   └── user_dao.py
├── controllers/                # validation + business logic
│   ├── customer_controller.py
│   ├── followup_controller.py
│   ├── contact_history_controller.py
│   └── auth_controller.py
├── views/                     # all Tkinter screens
│   ├── styles.py               # colors / fonts / shared widget styling
│   ├── login_view.py
│   ├── main_view.py            # sidebar + dashboard
│   ├── customer_view.py
│   ├── followup_view.py
│   ├── contact_history_view.py
│   └── customer_detail_view.py # the 360° view
└── utils/
    └── helpers.py
```

---

## Setup Instructions

### 1. Prerequisites
- Python 3.9 or newer
- MySQL Server 8.x (or MariaDB 10.x) installed and running

### 2. Install Python dependencies
```bash
pip install -r requirements.txt
```

### 3. Create the database
Run the schema file once, from the project folder, using the MySQL CLI:
```bash
mysql -u root -p < database/schema.sql
```
Or open `database/schema.sql` in MySQL Workbench and execute it.
This creates the `crm_system` database, all 4 tables, a default login, and a
handful of demo customers/follow-ups/contacts so the app isn't empty on first run.

### 4. Configure your credentials
Open `config.py` and update the password (and username/host if different):
```python
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "root",   # <-- change this
    "database": "crm_system",
}
```

### 5. (Optional but recommended) Verify everything works
```bash
python verify_setup.py
```
This runs 32 automated checks against your actual database — every add /
view / update / delete for every module — and cleans up after itself.
You should see `RESULTS: 32 passed, 0 failed`.

### 6. Run the application
```bash
python main.py
```

### Default login
```
Username: admin
Password: admin123
```

---

## Notes

- Passwords are stored as SHA-256 hashes, never in plain text.
- All SQL uses parameterized queries (no string-concatenated SQL anywhere),
  so the app is not vulnerable to SQL injection.
- Deleting a customer automatically removes their follow-ups and contact
  history too (`ON DELETE CASCADE` at the database level) — the app warns
  you about this before letting you confirm.
- If `tkcalendar` isn't installed for some reason, date fields automatically
  fall back to a plain text box (DD-MM-YYYY) instead of crashing.
- Window state: the main window opens maximized on Windows; on Linux/Mac it
  opens at a large fixed size if the OS/window manager doesn't support the
  "zoomed" state.

## Extending it further

A few natural next steps if you want to keep building on this for your
portfolio:
- Add a `reports/` module with charts (e.g. follow-ups completed per week)
- Add role-based permissions (Admin vs Sales Executive) using the `role`
  column already present in the `users` table
- Add email/SMS reminders for follow-ups due today
