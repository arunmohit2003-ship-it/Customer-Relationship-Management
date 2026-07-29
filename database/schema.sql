-- =========================================================
--  CRM PRO - DATABASE SCHEMA
--  Run this entire file once (MySQL CLI or MySQL Workbench)
--  to create the database, tables, the default login, and
--  a small set of demo records.
--
--  MySQL CLI:   mysql -u root -p < database/schema.sql
-- =========================================================

DROP DATABASE IF EXISTS crm_system;
CREATE DATABASE crm_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE crm_system;

-- ---------------------------------------------------------
-- Table: users  (login accounts for the CRM application)
-- ---------------------------------------------------------
CREATE TABLE users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    full_name     VARCHAR(100) NOT NULL,
    role          VARCHAR(30)  DEFAULT 'Sales Executive',
    created_date  DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Default login -> username: admin | password: admin123
-- (Password is stored as a SHA-256 hash, never in plain text.)
INSERT INTO users (username, password_hash, full_name, role) VALUES
('admin', '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9', 'Administrator', 'Admin');

-- ---------------------------------------------------------
-- Table: customers
-- ---------------------------------------------------------
CREATE TABLE customers (
    customer_id   INT AUTO_INCREMENT PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    company_name  VARCHAR(100),
    email         VARCHAR(100),
    phone         VARCHAR(20)  NOT NULL,
    address       VARCHAR(255),
    city          VARCHAR(50),
    state         VARCHAR(50),
    customer_type ENUM('Lead','Prospect','Active','Inactive') DEFAULT 'Lead',
    source        VARCHAR(50)  DEFAULT 'Other',
    assigned_to   VARCHAR(50),
    notes         TEXT,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_cust_name  (full_name),
    INDEX idx_cust_phone (phone)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Table: follow_ups
-- ---------------------------------------------------------
CREATE TABLE follow_ups (
    followup_id   INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT NOT NULL,
    followup_date DATE NOT NULL,
    followup_time TIME,
    purpose       VARCHAR(100),
    priority      ENUM('High','Medium','Low') DEFAULT 'Medium',
    status        ENUM('Pending','Completed','Cancelled','Rescheduled') DEFAULT 'Pending',
    remarks       TEXT,
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    INDEX idx_followup_date   (followup_date),
    INDEX idx_followup_status (status)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Table: contact_history
-- ---------------------------------------------------------
CREATE TABLE contact_history (
    history_id    INT AUTO_INCREMENT PRIMARY KEY,
    customer_id   INT NOT NULL,
    contact_date  DATE NOT NULL,
    contact_time  TIME,
    contact_type  ENUM('Call','Email','Meeting','WhatsApp','SMS','Visit') DEFAULT 'Call',
    subject       VARCHAR(150),
    description   TEXT,
    outcome       ENUM('Positive','Negative','Neutral','No Response') DEFAULT 'Neutral',
    handled_by    VARCHAR(50),
    created_date  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id) ON DELETE CASCADE,
    INDEX idx_contact_date (contact_date)
) ENGINE=InnoDB;

-- ---------------------------------------------------------
-- Demo data (safe to delete any time from inside the app)
-- ---------------------------------------------------------
INSERT INTO customers (full_name, company_name, email, phone, address, city, state, customer_type, source, assigned_to, notes) VALUES
('Rohan Sharma',    'Sharma Textiles',       'rohan.sharma@example.com',  '9811122233', '12 MG Road',        'Rewari',   'Haryana', 'Active',   'Referral',       'Aayush', 'Long-term client, prefers WhatsApp updates.'),
('Priya Verma',     'Verma Traders',         'priya.verma@example.com',   '9822233344', '45 Model Town',     'Delhi',    'Delhi',   'Prospect', 'Website',        'Aayush', 'Interested in bulk order, awaiting quotation.'),
('Karan Malhotra',  'Malhotra Auto Parts',   'karan.malhotra@example.com','9833344455', '78 Sector 14',      'Gurugram', 'Haryana', 'Lead',     'Cold Call',      'Aayush', 'First contact made last week.'),
('Neha Gupta',      'Gupta Electronics',     'neha.gupta@example.com',    '9844455566', '23 Civil Lines',    'Rewari',   'Haryana', 'Active',   'Referral',       'Aayush', 'Renewal due next quarter.'),
('Aditya Singh',    'Singh Constructions',   'aditya.singh@example.com',  '9855566677', '9 Ashok Vihar',     'Delhi',    'Delhi',   'Inactive', 'Social Media',   'Aayush', 'No response in last 3 months.');

INSERT INTO follow_ups (customer_id, followup_date, followup_time, purpose, priority, status, remarks) VALUES
(1, CURDATE(),                          '11:00:00', 'Renewal Discussion',   'High',   'Pending',   'Call to discuss annual contract renewal.'),
(2, CURDATE(),                          '15:30:00', 'Send Quotation',       'High',   'Pending',   'Prepare and send bulk order quotation.'),
(3, DATE_ADD(CURDATE(), INTERVAL 2 DAY),'10:00:00', 'Product Demo',         'Medium', 'Pending',   'Schedule an online demo.'),
(4, DATE_SUB(CURDATE(), INTERVAL 3 DAY),'12:00:00', 'Renewal Reminder',     'High',   'Completed', 'Reminder call done, customer agreed.'),
(5, DATE_SUB(CURDATE(), INTERVAL 10 DAY),'09:30:00','Re-engagement Call',   'Low',    'Cancelled', 'Customer asked not to be contacted for now.'),
(2, DATE_SUB(CURDATE(), INTERVAL 2 DAY),'09:00:00', 'Initial Requirement Call','Medium','Completed','Discussed requirement quantity and timelines.');

INSERT INTO contact_history (customer_id, contact_date, contact_time, contact_type, subject, description, outcome, handled_by) VALUES
(1, DATE_SUB(CURDATE(), INTERVAL 5 DAY),  '10:15:00', 'Call',    'Order Confirmation', 'Confirmed the last order details and delivery date.',      'Positive',    'Aayush'),
(2, DATE_SUB(CURDATE(), INTERVAL 2 DAY),  '14:00:00', 'Email',   'Product Catalogue',  'Sent the latest product catalogue with prices.',            'Neutral',     'Aayush'),
(4, DATE_SUB(CURDATE(), INTERVAL 1 DAY),  '16:45:00', 'Meeting', 'Contract Renewal',   'Met to discuss renewal terms, positive response.',          'Positive',    'Aayush'),
(5, DATE_SUB(CURDATE(), INTERVAL 30 DAY), '11:00:00', 'Call',    'Check-in Call',      'Tried to reach, no response.',                              'No Response', 'Aayush'),
(3, DATE_SUB(CURDATE(), INTERVAL 6 DAY),  '17:20:00', 'Call',    'First Introduction', 'Introduced our services and pricing.',                      'Neutral',     'Aayush');
