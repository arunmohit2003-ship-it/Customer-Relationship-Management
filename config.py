"""
config.py
---------
Central configuration for the CRM application.

IMPORTANT: Update DB_CONFIG below with YOUR local MySQL credentials
before running the application. These are the only lines you should
need to change to get the project running on a new machine.
"""

DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password":"202020",        # <-- change this to your MySQL root password
    "database": "crm_system",
}

APP_NAME = "CRM Pro - Customer Relationship Management"
APP_VERSION = "1.0.0"
