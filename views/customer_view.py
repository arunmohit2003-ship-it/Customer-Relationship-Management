"""
views/customer_view.py
------------------------
Customer management page: searchable/filterable list plus modal
Add/Edit forms. This is where module 1 of the CRM ("Customer
records") lives.
"""

import csv
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from controllers.customer_controller import CustomerController
from views.styles import Colors, Fonts, make_button
from views.customer_detail_view import CustomerDetailDialog
from utils.helpers import center_window


class CustomerView(tk.Frame):
    def __init__(self, parent, main_view):
        super().__init__(parent, bg=Colors.BG)
        self.main_view = main_view
        self.pack(fill="both", expand=True, padx=30, pady=25)
        self._build()
        self._load_data()

    # ------------------------------------------------------------------
    def _build(self):
        header = tk.Frame(self, bg=Colors.BG)
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Customers", font=Fonts.TITLE, bg=Colors.BG,
                 fg=Colors.TEXT_DARK).pack(side="left")
        make_button(header, "+ Add Customer", self._open_add_form).pack(side="right")
        make_button(header, "Export CSV", self._export_csv, bg=Colors.TEXT_MUTED
                    ).pack(side="right", padx=(0, 10))

        toolbar = tk.Frame(self, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                            highlightthickness=1)
        toolbar.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(toolbar, bg=Colors.CARD, padx=14, pady=12)
        inner.pack(fill="x")

        tk.Label(inner, text="Search:", font=Fonts.BODY, bg=Colors.CARD).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(inner, textvariable=self.search_var, font=Fonts.BODY,
                                 relief="solid", bd=1, width=30)
        search_entry.pack(side="left", padx=(8, 20), ipady=4)
        search_entry.bind("<KeyRelease>", lambda e: self._load_data())

        tk.Label(inner, text="Status:", font=Fonts.BODY, bg=Colors.CARD).pack(side="left")
        self.type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(inner, textvariable=self.type_var, state="readonly",
                                   values=["All", "Lead", "Prospect", "Active", "Inactive"], width=14)
        type_combo.pack(side="left", padx=(8, 0))
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        table_card = tk.Frame(self, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                               highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        columns = ("id", "name", "company", "phone", "email", "city", "type", "assigned")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "name": "Name", "company": "Company", "phone": "Phone",
                    "email": "Email", "city": "City", "type": "Status", "assigned": "Assigned To"}
        widths = {"id": 45, "name": 150, "company": 150, "phone": 110, "email": 190,
                  "city": 100, "type": 90, "assigned": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("Active", foreground=Colors.SUCCESS)
        self.tree.tag_configure("Lead", foreground=Colors.WARNING)
        self.tree.tag_configure("Prospect", foreground=Colors.PRIMARY)
        self.tree.tag_configure("Inactive", foreground=Colors.TEXT_MUTED)

        self.tree.bind("<Double-1>", lambda e: self._open_detail())

        action_bar = tk.Frame(self, bg=Colors.BG)
        action_bar.pack(fill="x", pady=(12, 0))
        make_button(action_bar, "View 360\u00b0", self._open_detail).pack(side="left")
        make_button(action_bar, "Edit", self._open_edit_form, bg=Colors.WARNING
                    ).pack(side="left", padx=10)
        make_button(action_bar, "Delete", self._delete_selected, bg=Colors.DANGER
                    ).pack(side="left")

    # ------------------------------------------------------------------
    def _load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            customers = CustomerController.get_all_customers(
                self.search_var.get().strip(), self.type_var.get())
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            return
        for c in customers:
            self.tree.insert("", "end", iid=str(c.customer_id), values=(
                c.customer_id, c.full_name, c.company_name or "-", c.phone,
                c.email or "-", c.city or "-", c.customer_type, c.assigned_to or "-"
            ), tags=(c.customer_type,))

    def _get_selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a customer from the list first.")
            return None
        return int(selection[0])

    # ------------------------------------------------------------------
    def _open_add_form(self):
        CustomerFormDialog(self, on_saved=self._load_data)

    def _open_edit_form(self):
        customer_id = self._get_selected_id()
        if customer_id is None:
            return
        CustomerFormDialog(self, customer_id=customer_id, on_saved=self._load_data)

    def _open_detail(self):
        customer_id = self._get_selected_id()
        if customer_id is None:
            return
        CustomerDetailDialog(self, customer_id, self.main_view)

    def _delete_selected(self):
        customer_id = self._get_selected_id()
        if customer_id is None:
            return
        if not messagebox.askyesno(
                "Confirm Delete",
                "Deleting this customer will also remove all of their follow-ups "
                "and contact history.\n\nAre you sure you want to continue?"):
            return
        try:
            CustomerController.delete_customer(customer_id)
            messagebox.showinfo("Deleted", "Customer deleted successfully.")
            self._load_data()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))

    def _export_csv(self):
        try:
            customers = CustomerController.get_all_customers(
                self.search_var.get().strip(), self.type_var.get())
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            return
        if not customers:
            messagebox.showinfo("Nothing to Export", "There are no customers to export.")
            return
        path = filedialog.asksaveasfilename(defaultextension=".csv",
                                             filetypes=[("CSV files", "*.csv")],
                                             initialfile="customers_export.csv")
        if not path:
            return
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Name", "Company", "Phone", "Email", "City",
                                  "State", "Status", "Source", "Assigned To", "Notes"])
                for c in customers:
                    writer.writerow([c.customer_id, c.full_name, c.company_name, c.phone,
                                      c.email, c.city, c.state, c.customer_type, c.source,
                                      c.assigned_to, c.notes])
            messagebox.showinfo("Export Complete", f"Customers exported to:\n{path}")
        except OSError as e:
            messagebox.showerror("Export Failed", str(e))


class CustomerFormDialog(tk.Toplevel):
    """Add or Edit a customer. If customer_id is given, loads existing data."""

    def __init__(self, parent, on_saved, customer_id=None):
        super().__init__(parent)
        self.on_saved = on_saved
        self.customer_id = customer_id
        self.dialog_title = "Edit Customer" if customer_id else "Add New Customer"
        self.title(self.dialog_title)
        self.configure(bg=Colors.WHITE)
        self.resizable(False, False)
        center_window(self, 480, 640)
        self._build()
        if customer_id:
            self._load_existing()
        self.transient(parent.winfo_toplevel())
        self.grab_set()

    def _build(self):
        tk.Label(self, text=self.dialog_title, font=Fonts.H2, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK).pack(anchor="w", padx=24, pady=(20, 16))

        form = tk.Frame(self, bg=Colors.WHITE)
        form.pack(fill="both", expand=True, padx=24)

        self.entries = {}
        fields = [
            ("full_name", "Full Name *"),
            ("company_name", "Company Name"),
            ("phone", "Phone *"),
            ("email", "Email"),
            ("city", "City"),
            ("state", "State"),
            ("address", "Address"),
        ]
        for key, label in fields:
            tk.Label(form, text=label, font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                     fg=Colors.TEXT_DARK, anchor="w").pack(fill="x", pady=(6, 2))
            entry = tk.Entry(form, font=Fonts.BODY, relief="solid", bd=1)
            entry.pack(fill="x", ipady=5)
            self.entries[key] = entry

        row2 = tk.Frame(form, bg=Colors.WHITE)
        row2.pack(fill="x", pady=(6, 2))
        left = tk.Frame(row2, bg=Colors.WHITE)
        left.pack(side="left", fill="x", expand=True, padx=(0, 6))
        right = tk.Frame(row2, bg=Colors.WHITE)
        right.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(left, text="Status", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x")
        self.type_var = tk.StringVar(value="Lead")
        ttk.Combobox(left, textvariable=self.type_var, state="readonly",
                     values=["Lead", "Prospect", "Active", "Inactive"]).pack(fill="x", ipady=3)

        tk.Label(right, text="Source", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x")
        self.source_var = tk.StringVar(value="Other")
        ttk.Combobox(right, textvariable=self.source_var, state="readonly",
                     values=["Referral", "Website", "Cold Call", "Social Media",
                             "Advertisement", "Other"]).pack(fill="x", ipady=3)

        tk.Label(form, text="Assigned To", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x", pady=(6, 2))
        self.assigned_entry = tk.Entry(form, font=Fonts.BODY, relief="solid", bd=1)
        self.assigned_entry.pack(fill="x", ipady=5)

        tk.Label(form, text="Notes", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x", pady=(6, 2))
        self.notes_text = tk.Text(form, font=Fonts.BODY, relief="solid", bd=1, height=3)
        self.notes_text.pack(fill="x")

        btn_row = tk.Frame(self, bg=Colors.WHITE)
        btn_row.pack(fill="x", padx=24, pady=20)
        make_button(btn_row, "Save Customer", self._save).pack(side="right")
        make_button(btn_row, "Cancel", self.destroy, bg=Colors.TEXT_MUTED
                    ).pack(side="right", padx=(0, 10))

    def _load_existing(self):
        try:
            c = CustomerController.get_customer(self.customer_id)
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.destroy()
            return
        if not c:
            messagebox.showerror("Not Found", "This customer no longer exists.")
            self.destroy()
            return
        self.entries["full_name"].insert(0, c.full_name)
        self.entries["company_name"].insert(0, c.company_name or "")
        self.entries["phone"].insert(0, c.phone)
        self.entries["email"].insert(0, c.email or "")
        self.entries["city"].insert(0, c.city or "")
        self.entries["state"].insert(0, c.state or "")
        self.entries["address"].insert(0, c.address or "")
        self.type_var.set(c.customer_type)
        self.source_var.set(c.source or "Other")
        self.assigned_entry.insert(0, c.assigned_to or "")
        self.notes_text.insert("1.0", c.notes or "")

    def _save(self):
        values = {k: e.get() for k, e in self.entries.items()}
        try:
            if self.customer_id:
                CustomerController.update_customer(
                    self.customer_id, values["full_name"], values["company_name"],
                    values["email"], values["phone"], values["address"], values["city"],
                    values["state"], self.type_var.get(), self.source_var.get(),
                    self.assigned_entry.get(), self.notes_text.get("1.0", "end").strip())
                messagebox.showinfo("Success", "Customer updated successfully.")
            else:
                CustomerController.add_customer(
                    values["full_name"], values["company_name"], values["email"],
                    values["phone"], values["address"], values["city"], values["state"],
                    self.type_var.get(), self.source_var.get(), self.assigned_entry.get(),
                    self.notes_text.get("1.0", "end").strip())
                messagebox.showinfo("Success", "Customer added successfully.")
            self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
