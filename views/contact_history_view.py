"""
views/contact_history_view.py
--------------------------------
Contact History page: list with type filter plus modal Add/Edit
forms. This is module 3 of the CRM ("Contact history").
"""

import tkinter as tk
from datetime import date, time, datetime
from tkinter import ttk, messagebox

try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

from controllers.contact_history_controller import ContactHistoryController
from controllers.customer_controller import CustomerController
from views.styles import Colors, Fonts, make_button
from utils.helpers import center_window, format_date


class ContactHistoryView(tk.Frame):
    def __init__(self, parent, main_view, preselect_customer_id=None):
        super().__init__(parent, bg=Colors.BG)
        self.main_view = main_view
        self.preselect_customer_id = preselect_customer_id
        self.pack(fill="both", expand=True, padx=30, pady=25)
        self._build()
        self._load_data()
        if preselect_customer_id:
            self.after(150, self._open_add_form)

    def _build(self):
        header = tk.Frame(self, bg=Colors.BG)
        header.pack(fill="x", pady=(0, 16))
        tk.Label(header, text="Contact History", font=Fonts.TITLE, bg=Colors.BG,
                 fg=Colors.TEXT_DARK).pack(side="left")
        make_button(header, "+ Log Contact", self._open_add_form).pack(side="right")

        toolbar = tk.Frame(self, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                            highlightthickness=1)
        toolbar.pack(fill="x", pady=(0, 14))
        inner = tk.Frame(toolbar, bg=Colors.CARD, padx=14, pady=12)
        inner.pack(fill="x")

        tk.Label(inner, text="Search:", font=Fonts.BODY, bg=Colors.CARD).pack(side="left")
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(inner, textvariable=self.search_var, font=Fonts.BODY,
                                 relief="solid", bd=1, width=26)
        search_entry.pack(side="left", padx=(8, 20), ipady=4)
        search_entry.bind("<KeyRelease>", lambda e: self._load_data())

        tk.Label(inner, text="Type:", font=Fonts.BODY, bg=Colors.CARD).pack(side="left")
        self.type_var = tk.StringVar(value="All")
        type_combo = ttk.Combobox(inner, textvariable=self.type_var, state="readonly",
                                   values=["All", "Call", "Email", "Meeting", "WhatsApp", "SMS", "Visit"],
                                   width=14)
        type_combo.pack(side="left", padx=(8, 0))
        type_combo.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        table_card = tk.Frame(self, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                               highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        columns = ("id", "customer", "date", "type", "subject", "outcome", "handled_by")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "customer": "Customer", "date": "Date", "type": "Type",
                    "subject": "Subject", "outcome": "Outcome", "handled_by": "Handled By"}
        widths = {"id": 45, "customer": 150, "date": 100, "type": 90, "subject": 210,
                  "outcome": 100, "handled_by": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("Positive", foreground=Colors.SUCCESS)
        self.tree.tag_configure("Negative", foreground=Colors.DANGER)
        self.tree.tag_configure("Neutral", foreground=Colors.WARNING)
        self.tree.tag_configure("No Response", foreground=Colors.TEXT_MUTED)

        action_bar = tk.Frame(self, bg=Colors.BG)
        action_bar.pack(fill="x", pady=(12, 0))
        make_button(action_bar, "Edit", self._open_edit_form, bg=Colors.PRIMARY).pack(side="left")
        make_button(action_bar, "Delete", self._delete_selected, bg=Colors.DANGER
                    ).pack(side="left", padx=10)

    def _load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            contacts = ContactHistoryController.get_all_contacts(
                self.type_var.get(), self.search_var.get().strip())
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            return
        for h in contacts:
            self.tree.insert("", "end", iid=str(h.history_id), values=(
                h.history_id, h.customer_name, format_date(h.contact_date), h.contact_type,
                h.subject, h.outcome, h.handled_by or "-"
            ), tags=(h.outcome,))

    def _get_selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a record from the list first.")
            return None
        return int(selection[0])

    def _open_add_form(self):
        ContactHistoryFormDialog(self, on_saved=self._load_data,
                                  preselect_customer_id=self.preselect_customer_id)

    def _open_edit_form(self):
        history_id = self._get_selected_id()
        if history_id is None:
            return
        ContactHistoryFormDialog(self, on_saved=self._load_data, history_id=history_id)

    def _delete_selected(self):
        history_id = self._get_selected_id()
        if history_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this contact record permanently?"):
            return
        try:
            ContactHistoryController.delete_contact(history_id)
            self._load_data()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))


class ContactHistoryFormDialog(tk.Toplevel):
    def __init__(self, parent, on_saved, history_id=None, preselect_customer_id=None):
        super().__init__(parent)
        self.on_saved = on_saved
        self.history_id = history_id
        self.dialog_title = "Edit Contact Record" if history_id else "Log New Contact"
        self.title(self.dialog_title)
        self.configure(bg=Colors.WHITE)
        self.resizable(False, False)
        center_window(self, 460, 660)

        try:
            self.customers = CustomerController.get_customer_names()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.customers = []

        self._build()
        if history_id:
            self._load_existing()
        elif preselect_customer_id:
            self._preselect(preselect_customer_id)

        self.transient(parent.winfo_toplevel())
        self.grab_set()

    def _build(self):
        tk.Label(self, text=self.dialog_title, font=Fonts.H2, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK).pack(anchor="w", padx=24, pady=(20, 16))

        form = tk.Frame(self, bg=Colors.WHITE)
        form.pack(fill="both", expand=True, padx=24)

        tk.Label(form, text="Customer *", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(4, 2))
        self.customer_names = [f"{cid} - {name}" for cid, name in self.customers]
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(form, textvariable=self.customer_var, state="readonly",
                                            values=self.customer_names)
        self.customer_combo.pack(fill="x", ipady=4)

        row1 = tk.Frame(form, bg=Colors.WHITE)
        row1.pack(fill="x", pady=(10, 2))
        date_col = tk.Frame(row1, bg=Colors.WHITE)
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        time_col = tk.Frame(row1, bg=Colors.WHITE)
        time_col.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(date_col, text="Contact Date *", font=Fonts.BODY_BOLD,
                 bg=Colors.WHITE, anchor="w").pack(fill="x")
        if HAS_CALENDAR:
            self.date_picker = DateEntry(date_col, date_pattern="dd-mm-yyyy",
                                          background=Colors.PRIMARY, foreground="white",
                                          borderwidth=1)
            self.date_picker.pack(fill="x", ipady=3)
        else:
            self.date_picker = tk.Entry(date_col, font=Fonts.BODY, relief="solid", bd=1)
            self.date_picker.insert(0, date.today().strftime("%d-%m-%Y"))
            self.date_picker.pack(fill="x", ipady=5)

        tk.Label(time_col, text="Time", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x")
        time_frame = tk.Frame(time_col, bg=Colors.WHITE)
        time_frame.pack(fill="x")
        now = datetime.now()
        self.hour_var = tk.StringVar(value=f"{now.hour:02d}")
        self.min_var = tk.StringVar(value=f"{(now.minute // 15) * 15 % 60:02d}")
        ttk.Combobox(time_frame, textvariable=self.hour_var, state="readonly", width=4,
                     values=[f"{h:02d}" for h in range(24)]).pack(side="left")
        tk.Label(time_frame, text=":", bg=Colors.WHITE).pack(side="left")
        ttk.Combobox(time_frame, textvariable=self.min_var, state="readonly", width=4,
                     values=["00", "15", "30", "45"]).pack(side="left")

        row2 = tk.Frame(form, bg=Colors.WHITE)
        row2.pack(fill="x", pady=(10, 2))
        type_col = tk.Frame(row2, bg=Colors.WHITE)
        type_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        handled_col = tk.Frame(row2, bg=Colors.WHITE)
        handled_col.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(type_col, text="Contact Type", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x")
        self.type_var = tk.StringVar(value="Call")
        ttk.Combobox(type_col, textvariable=self.type_var, state="readonly",
                     values=["Call", "Email", "Meeting", "WhatsApp", "SMS", "Visit"]
                     ).pack(fill="x", ipady=3)

        tk.Label(handled_col, text="Handled By", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x")
        self.handled_entry = tk.Entry(handled_col, font=Fonts.BODY, relief="solid", bd=1)
        self.handled_entry.pack(fill="x", ipady=5)

        tk.Label(form, text="Subject *", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.subject_entry = tk.Entry(form, font=Fonts.BODY, relief="solid", bd=1)
        self.subject_entry.pack(fill="x", ipady=5)

        tk.Label(form, text="Description", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.desc_text = tk.Text(form, font=Fonts.BODY, relief="solid", bd=1, height=3)
        self.desc_text.pack(fill="x")

        tk.Label(form, text="Outcome", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.outcome_var = tk.StringVar(value="Neutral")
        ttk.Combobox(form, textvariable=self.outcome_var, state="readonly",
                     values=["Positive", "Negative", "Neutral", "No Response"]).pack(fill="x", ipady=3)

        btn_row = tk.Frame(self, bg=Colors.WHITE)
        btn_row.pack(fill="x", padx=24, pady=20)
        make_button(btn_row, "Save", self._save).pack(side="right")
        make_button(btn_row, "Cancel", self.destroy, bg=Colors.TEXT_MUTED
                    ).pack(side="right", padx=(0, 10))

    def _preselect(self, customer_id):
        for label in self.customer_names:
            if label.startswith(f"{customer_id} -"):
                self.customer_var.set(label)
                break

    def _load_existing(self):
        try:
            h = ContactHistoryController.get_contact(self.history_id)
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.destroy()
            return
        if not h:
            messagebox.showerror("Not Found", "This record no longer exists.")
            self.destroy()
            return
        self._preselect(h.customer_id)
        if HAS_CALENDAR:
            self.date_picker.set_date(h.contact_date)
        else:
            self.date_picker.delete(0, "end")
            self.date_picker.insert(0, format_date(h.contact_date))
        if h.contact_time:
            secs = h.contact_time.seconds if hasattr(h.contact_time, "seconds") else 0
            self.hour_var.set(f"{(secs // 3600) % 24:02d}")
            self.min_var.set(f"{(secs % 3600) // 60:02d}")
        self.type_var.set(h.contact_type)
        self.subject_entry.insert(0, h.subject or "")
        self.desc_text.insert("1.0", h.description or "")
        self.outcome_var.set(h.outcome)
        self.handled_entry.insert(0, h.handled_by or "")

    def _get_customer_id(self):
        label = self.customer_var.get()
        if not label:
            return None
        return int(label.split(" - ", 1)[0])

    def _get_date_value(self):
        if HAS_CALENDAR:
            return self.date_picker.get_date()
        raw = self.date_picker.get().strip()
        try:
            return datetime.strptime(raw, "%d-%m-%Y").date()
        except ValueError:
            raise ValueError("Enter the date as DD-MM-YYYY.")

    def _save(self):
        try:
            customer_id = self._get_customer_id()
            contact_date = self._get_date_value()
            contact_time = time(int(self.hour_var.get()), int(self.min_var.get()))
            contact_type = self.type_var.get()
            subject = self.subject_entry.get()
            description = self.desc_text.get("1.0", "end").strip()
            outcome = self.outcome_var.get()
            handled_by = self.handled_entry.get()

            if self.history_id:
                ContactHistoryController.update_contact(
                    self.history_id, customer_id, contact_date, contact_time, contact_type,
                    subject, description, outcome, handled_by)
                messagebox.showinfo("Success", "Contact record updated successfully.")
            else:
                ContactHistoryController.log_contact(
                    customer_id, contact_date, contact_time, contact_type, subject,
                    description, outcome, handled_by)
                messagebox.showinfo("Success", "Contact logged successfully.")
            self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
