"""
views/customer_detail_view.py
--------------------------------
Customer 360-degree view: shows profile info plus all related
follow-ups and contact history for a single customer, in one window.
This is what ties all three CRM modules together.
"""

import tkinter as tk
from tkinter import ttk, messagebox

from controllers.customer_controller import CustomerController
from controllers.followup_controller import FollowUpController
from controllers.contact_history_controller import ContactHistoryController
from views.styles import Colors, Fonts, make_button, status_color
from utils.helpers import center_window, format_date, format_time


class CustomerDetailDialog(tk.Toplevel):
    def __init__(self, parent, customer_id, main_view):
        super().__init__(parent)
        self.customer_id = customer_id
        self.main_view = main_view
        self.title("Customer 360\u00b0 View")
        self.configure(bg=Colors.BG)
        center_window(self, 780, 620)
        self.transient(parent.winfo_toplevel())
        self.grab_set()
        self._build()

    def _build(self):
        try:
            customer = CustomerController.get_customer(self.customer_id)
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.destroy()
            return
        if not customer:
            messagebox.showerror("Not Found", "This customer no longer exists.")
            self.destroy()
            return

        header = tk.Frame(self, bg=Colors.SIDEBAR, padx=24, pady=18)
        header.pack(fill="x")
        tk.Label(header, text=customer.full_name, font=Fonts.H2, bg=Colors.SIDEBAR,
                 fg=Colors.WHITE).pack(anchor="w")
        subtitle = customer.company_name or "Individual Customer"
        tk.Label(header, text=subtitle, font=Fonts.BODY, bg=Colors.SIDEBAR,
                 fg="#9AA9C0").pack(anchor="w")

        info_bar = tk.Frame(self, bg=Colors.CARD, padx=24, pady=14)
        info_bar.pack(fill="x")
        details = [
            ("Phone", customer.phone), ("Email", customer.email or "-"),
            ("City", customer.city or "-"), ("Status", customer.customer_type),
        ]
        for i, (label, value) in enumerate(details):
            col = tk.Frame(info_bar, bg=Colors.CARD)
            col.grid(row=0, column=i, sticky="w", padx=(0 if i == 0 else 24, 0))
            tk.Label(col, text=label, font=Fonts.SMALL, bg=Colors.CARD,
                     fg=Colors.TEXT_MUTED).pack(anchor="w")
            fg = status_color(value) if label == "Status" else Colors.TEXT_DARK
            tk.Label(col, text=value, font=Fonts.BODY_BOLD, bg=Colors.CARD, fg=fg).pack(anchor="w")

        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=20, pady=16)

        followups_tab = tk.Frame(notebook, bg=Colors.BG)
        contacts_tab = tk.Frame(notebook, bg=Colors.BG)
        notebook.add(followups_tab, text="  Follow-ups  ")
        notebook.add(contacts_tab, text="  Contact History  ")

        self._build_followups_tab(followups_tab)
        self._build_contacts_tab(contacts_tab)

        btn_row = tk.Frame(self, bg=Colors.BG)
        btn_row.pack(fill="x", padx=20, pady=(0, 16))
        make_button(btn_row, "+ Schedule Follow-up", self._add_followup).pack(side="left")
        make_button(btn_row, "+ Log Contact", self._add_contact, bg=Colors.TEXT_MUTED
                    ).pack(side="left", padx=10)
        make_button(btn_row, "Close", self.destroy, bg=Colors.DANGER).pack(side="right")

    def _build_followups_tab(self, tab):
        columns = ("date", "time", "purpose", "priority", "status")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=8)
        headings = {"date": "Date", "time": "Time", "purpose": "Purpose",
                    "priority": "Priority", "status": "Status"}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=130, anchor="w")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        try:
            followups = FollowUpController.get_followups_for_customer(self.customer_id)
        except (ConnectionError, RuntimeError):
            followups = []
        for f in followups:
            tree.insert("", "end", values=(format_date(f.followup_date), format_time(f.followup_time),
                                            f.purpose, f.priority, f.status))
        if not followups:
            tk.Label(tab, text="No follow-ups scheduled yet for this customer.",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(pady=20)

    def _build_contacts_tab(self, tab):
        columns = ("date", "type", "subject", "outcome", "handled_by")
        tree = ttk.Treeview(tab, columns=columns, show="headings", height=8)
        headings = {"date": "Date", "type": "Type", "subject": "Subject",
                    "outcome": "Outcome", "handled_by": "Handled By"}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=130, anchor="w")
        tree.pack(fill="both", expand=True, padx=4, pady=4)

        try:
            contacts = ContactHistoryController.get_contacts_for_customer(self.customer_id)
        except (ConnectionError, RuntimeError):
            contacts = []
        for h in contacts:
            tree.insert("", "end", values=(format_date(h.contact_date), h.contact_type,
                                            h.subject, h.outcome, h.handled_by))
        if not contacts:
            tk.Label(tab, text="No contact history logged yet for this customer.",
                     font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(pady=20)

    def _add_followup(self):
        self.destroy()
        self.main_view.show_followups(customer_id=self.customer_id)

    def _add_contact(self):
        self.destroy()
        self.main_view.show_contacts(customer_id=self.customer_id)
