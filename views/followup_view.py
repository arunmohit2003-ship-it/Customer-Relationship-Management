"""
views/followup_view.py
------------------------
Follow-up management page: list with status/priority visibility plus
modal Add/Edit forms. This is module 2 of the CRM ("Follow-up status").
"""

import tkinter as tk
from datetime import date, time, datetime
from tkinter import ttk, messagebox

try:
    from tkcalendar import DateEntry
    HAS_CALENDAR = True
except ImportError:
    HAS_CALENDAR = False

from controllers.followup_controller import FollowUpController
from controllers.customer_controller import CustomerController
from views.styles import Colors, Fonts, make_button
from utils.helpers import center_window, format_date, format_time


class FollowUpView(tk.Frame):
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
        tk.Label(header, text="Follow-ups", font=Fonts.TITLE, bg=Colors.BG,
                 fg=Colors.TEXT_DARK).pack(side="left")
        make_button(header, "+ Schedule Follow-up", self._open_add_form).pack(side="right")

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

        tk.Label(inner, text="Status:", font=Fonts.BODY, bg=Colors.CARD).pack(side="left")
        self.status_var = tk.StringVar(value="All")
        status_combo = ttk.Combobox(inner, textvariable=self.status_var, state="readonly",
                                     values=["All", "Pending", "Completed", "Cancelled", "Rescheduled"],
                                     width=14)
        status_combo.pack(side="left", padx=(8, 0))
        status_combo.bind("<<ComboboxSelected>>", lambda e: self._load_data())

        legend = tk.Label(inner, text="\u25A0 Overdue rows are highlighted", font=Fonts.SMALL,
                           bg=Colors.CARD, fg=Colors.DANGER)
        legend.pack(side="right")

        table_card = tk.Frame(self, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                               highlightthickness=1)
        table_card.pack(fill="both", expand=True)

        columns = ("id", "customer", "date", "time", "purpose", "priority", "status")
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings", selectmode="browse")
        headings = {"id": "ID", "customer": "Customer", "date": "Date", "time": "Time",
                    "purpose": "Purpose", "priority": "Priority", "status": "Status"}
        widths = {"id": 45, "customer": 150, "date": 100, "time": 90, "purpose": 170,
                  "priority": 80, "status": 100}
        for col in columns:
            self.tree.heading(col, text=headings[col])
            self.tree.column(col, width=widths[col], anchor="w")

        vsb = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(2, 0), pady=2)
        vsb.pack(side="right", fill="y")

        self.tree.tag_configure("Pending", foreground=Colors.WARNING)
        self.tree.tag_configure("Completed", foreground=Colors.SUCCESS)
        self.tree.tag_configure("Cancelled", foreground=Colors.DANGER)
        self.tree.tag_configure("Rescheduled", foreground=Colors.PRIMARY)
        self.tree.tag_configure("overdue_row", background="#FDEDEE")

        action_bar = tk.Frame(self, bg=Colors.BG)
        action_bar.pack(fill="x", pady=(12, 0))
        make_button(action_bar, "Edit", self._open_edit_form, bg=Colors.PRIMARY).pack(side="left")
        make_button(action_bar, "Mark Completed", lambda: self._change_status("Completed"),
                    bg=Colors.SUCCESS).pack(side="left", padx=10)
        make_button(action_bar, "Cancel Follow-up", lambda: self._change_status("Cancelled"),
                    bg=Colors.WARNING).pack(side="left")
        make_button(action_bar, "Delete", self._delete_selected, bg=Colors.DANGER
                    ).pack(side="left", padx=10)

    def _load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            followups = FollowUpController.get_all_followups(
                self.status_var.get(), self.search_var.get().strip())
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            return
        today = date.today()
        for f in followups:
            is_overdue = (f.status == "Pending" and f.followup_date and f.followup_date < today)
            tags = (f.status, "overdue_row") if is_overdue else (f.status,)
            self.tree.insert("", "end", iid=str(f.followup_id), values=(
                f.followup_id, f.customer_name, format_date(f.followup_date),
                format_time(f.followup_time), f.purpose, f.priority, f.status
            ), tags=tags)

    def _get_selected_id(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a follow-up from the list first.")
            return None
        return int(selection[0])

    def _open_add_form(self):
        FollowUpFormDialog(self, on_saved=self._load_data,
                            preselect_customer_id=self.preselect_customer_id)

    def _open_edit_form(self):
        followup_id = self._get_selected_id()
        if followup_id is None:
            return
        FollowUpFormDialog(self, on_saved=self._load_data, followup_id=followup_id)

    def _change_status(self, status):
        followup_id = self._get_selected_id()
        if followup_id is None:
            return
        try:
            FollowUpController.mark_status(followup_id, status)
            self._load_data()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))

    def _delete_selected(self):
        followup_id = self._get_selected_id()
        if followup_id is None:
            return
        if not messagebox.askyesno("Confirm Delete", "Delete this follow-up permanently?"):
            return
        try:
            FollowUpController.delete_followup(followup_id)
            self._load_data()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))


class FollowUpFormDialog(tk.Toplevel):
    def __init__(self, parent, on_saved, followup_id=None, preselect_customer_id=None):
        super().__init__(parent)
        self.on_saved = on_saved
        self.followup_id = followup_id
        self.dialog_title = "Edit Follow-up" if followup_id else "Schedule Follow-up"
        self.title(self.dialog_title)
        self.configure(bg=Colors.WHITE)
        self.resizable(False, False)
        center_window(self, 460, 610)

        try:
            self.customers = CustomerController.get_customer_names()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.customers = []

        self._build()
        if followup_id:
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

        date_row = tk.Frame(form, bg=Colors.WHITE)
        date_row.pack(fill="x", pady=(10, 2))
        date_col = tk.Frame(date_row, bg=Colors.WHITE)
        date_col.pack(side="left", fill="x", expand=True, padx=(0, 6))
        time_col = tk.Frame(date_row, bg=Colors.WHITE)
        time_col.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(date_col, text="Follow-up Date *", font=Fonts.BODY_BOLD,
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
        self.hour_var = tk.StringVar(value="10")
        self.min_var = tk.StringVar(value="00")
        ttk.Combobox(time_frame, textvariable=self.hour_var, state="readonly", width=4,
                     values=[f"{h:02d}" for h in range(24)]).pack(side="left")
        tk.Label(time_frame, text=":", bg=Colors.WHITE).pack(side="left")
        ttk.Combobox(time_frame, textvariable=self.min_var, state="readonly", width=4,
                     values=["00", "15", "30", "45"]).pack(side="left")

        tk.Label(form, text="Purpose *", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.purpose_entry = tk.Entry(form, font=Fonts.BODY, relief="solid", bd=1)
        self.purpose_entry.pack(fill="x", ipady=5)

        row3 = tk.Frame(form, bg=Colors.WHITE)
        row3.pack(fill="x", pady=(10, 2))
        pcol = tk.Frame(row3, bg=Colors.WHITE)
        pcol.pack(side="left", fill="x", expand=True, padx=(0, 6))
        scol = tk.Frame(row3, bg=Colors.WHITE)
        scol.pack(side="left", fill="x", expand=True, padx=(6, 0))

        tk.Label(pcol, text="Priority", font=Fonts.BODY_BOLD, bg=Colors.WHITE, anchor="w").pack(fill="x")
        self.priority_var = tk.StringVar(value="Medium")
        ttk.Combobox(pcol, textvariable=self.priority_var, state="readonly",
                     values=["High", "Medium", "Low"]).pack(fill="x", ipady=3)

        tk.Label(scol, text="Status", font=Fonts.BODY_BOLD, bg=Colors.WHITE, anchor="w").pack(fill="x")
        self.status_var = tk.StringVar(value="Pending")
        ttk.Combobox(scol, textvariable=self.status_var, state="readonly",
                     values=["Pending", "Completed", "Cancelled", "Rescheduled"]).pack(fill="x", ipady=3)

        tk.Label(form, text="Remarks", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 anchor="w").pack(fill="x", pady=(10, 2))
        self.remarks_text = tk.Text(form, font=Fonts.BODY, relief="solid", bd=1, height=3)
        self.remarks_text.pack(fill="x")

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
            f = FollowUpController.get_followup(self.followup_id)
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            self.destroy()
            return
        if not f:
            messagebox.showerror("Not Found", "This follow-up no longer exists.")
            self.destroy()
            return
        self._preselect(f.customer_id)
        if HAS_CALENDAR:
            self.date_picker.set_date(f.followup_date)
        else:
            self.date_picker.delete(0, "end")
            self.date_picker.insert(0, format_date(f.followup_date))
        if f.followup_time:
            secs = f.followup_time.seconds if hasattr(f.followup_time, "seconds") else 0
            self.hour_var.set(f"{(secs // 3600) % 24:02d}")
            self.min_var.set(f"{(secs % 3600) // 60:02d}")
        self.purpose_entry.insert(0, f.purpose or "")
        self.priority_var.set(f.priority)
        self.status_var.set(f.status)
        self.remarks_text.insert("1.0", f.remarks or "")

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
            followup_date = self._get_date_value()
            followup_time = time(int(self.hour_var.get()), int(self.min_var.get()))
            purpose = self.purpose_entry.get()
            priority = self.priority_var.get()
            status = self.status_var.get()
            remarks = self.remarks_text.get("1.0", "end").strip()

            if self.followup_id:
                FollowUpController.update_followup(
                    self.followup_id, customer_id, followup_date, followup_time,
                    purpose, priority, status, remarks)
                messagebox.showinfo("Success", "Follow-up updated successfully.")
            else:
                FollowUpController.schedule_followup(
                    customer_id, followup_date, followup_time, purpose, priority, status, remarks)
                messagebox.showinfo("Success", "Follow-up scheduled successfully.")
            self.on_saved()
            self.destroy()
        except ValueError as e:
            messagebox.showerror("Validation Error", str(e))
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
