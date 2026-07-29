"""
views/main_view.py
--------------------
The main application shell shown after a successful login. This is a
tk.Frame that lives inside the single persistent root window. It owns
the sidebar navigation and swaps content pages (Dashboard / Customers /
Follow-ups / Contact History) inside itself.
"""

import tkinter as tk
from tkinter import messagebox

from views.styles import Colors, Fonts, make_button
from views.customer_view import CustomerView
from views.followup_view import FollowUpView
from views.contact_history_view import ContactHistoryView
from utils.helpers import format_date, format_time

from controllers.customer_controller import CustomerController
from controllers.followup_controller import FollowUpController
from controllers.contact_history_controller import ContactHistoryController


class MainFrame(tk.Frame):
    def __init__(self, parent, user, on_logout):
        super().__init__(parent, bg=Colors.BG)
        self.user = user
        self.on_logout = on_logout
        self.nav_buttons = {}
        self.current_page = None

        self._build_sidebar()
        self._build_content_area()
        self.show_dashboard()

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------
    def _build_sidebar(self):
        sidebar = tk.Frame(self, bg=Colors.SIDEBAR, width=230)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        tk.Label(sidebar, text="CRM PRO", font=("Segoe UI", 18, "bold"),
                 bg=Colors.SIDEBAR, fg=Colors.WHITE).pack(pady=(28, 2))
        tk.Label(sidebar, text="Sales Workspace", font=Fonts.SMALL,
                 bg=Colors.SIDEBAR, fg="#9AA9C0").pack(pady=(0, 20))

        tk.Frame(sidebar, bg="#2C3E63", height=1).pack(fill="x", padx=20, pady=(0, 10))

        nav_items = [
            ("dashboard", "  \u25A0  Dashboard", self.show_dashboard),
            ("customers", "  \u25A0  Customers", self.show_customers),
            ("followups", "  \u25A0  Follow-ups", self.show_followups),
            ("contacts", "  \u25A0  Contact History", self.show_contacts),
        ]
        for key, label, command in nav_items:
            btn = tk.Button(sidebar, text=label, anchor="w", command=command,
                             bg=Colors.SIDEBAR, fg=Colors.WHITE, font=Fonts.SIDEBAR,
                             relief="flat", bd=0, padx=24, pady=12, cursor="hand2",
                             activebackground=Colors.SIDEBAR_HOVER, activeforeground=Colors.WHITE)
            btn.pack(fill="x")
            btn.bind("<Enter>", lambda e, b=btn, k=key: self._on_hover(b, k, True))
            btn.bind("<Leave>", lambda e, b=btn, k=key: self._on_hover(b, k, False))
            self.nav_buttons[key] = btn

        bottom = tk.Frame(sidebar, bg=Colors.SIDEBAR)
        bottom.pack(side="bottom", fill="x", pady=20)
        tk.Label(bottom, text="Logged in as", font=Fonts.SMALL,
                 bg=Colors.SIDEBAR, fg="#9AA9C0").pack()
        tk.Label(bottom, text=self.user.get("full_name", "User"), font=Fonts.BODY_BOLD,
                 bg=Colors.SIDEBAR, fg=Colors.WHITE).pack(pady=(0, 10))
        logout_btn = make_button(bottom, "Logout", self._logout, bg="#B33951",
                                  hover_bg="#8F2D41", width=16)
        logout_btn.pack()

    def _on_hover(self, btn, key, entering):
        if self.current_page == key:
            return
        btn["bg"] = Colors.SIDEBAR_HOVER if entering else Colors.SIDEBAR

    def _set_active_nav(self, key):
        for k, btn in self.nav_buttons.items():
            btn["bg"] = Colors.SIDEBAR_ACTIVE if k == key else Colors.SIDEBAR
        self.current_page = key

    def _build_content_area(self):
        self.content = tk.Frame(self, bg=Colors.BG)
        self.content.pack(side="left", fill="both", expand=True)

    def _clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    # ------------------------------------------------------------------
    # Pages
    # ------------------------------------------------------------------
    def show_dashboard(self):
        self._set_active_nav("dashboard")
        self._clear_content()
        DashboardPage(self.content, self)

    def show_customers(self):
        self._set_active_nav("customers")
        self._clear_content()
        CustomerView(self.content, self)

    def show_followups(self, customer_id=None):
        self._set_active_nav("followups")
        self._clear_content()
        FollowUpView(self.content, self, preselect_customer_id=customer_id)

    def show_contacts(self, customer_id=None):
        self._set_active_nav("contacts")
        self._clear_content()
        ContactHistoryView(self.content, self, preselect_customer_id=customer_id)

    def _logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.on_logout()


class DashboardPage(tk.Frame):
    """Home page: KPI cards + upcoming follow-ups + recent contact history."""

    def __init__(self, parent, main_view):
        super().__init__(parent, bg=Colors.BG)
        self.main_view = main_view
        self.pack(fill="both", expand=True, padx=30, pady=25)
        self._build()

    def _build(self):
        tk.Label(self, text=f"Welcome back, {self.main_view.user.get('full_name', '')}",
                 font=Fonts.TITLE, bg=Colors.BG, fg=Colors.TEXT_DARK).pack(anchor="w")
        tk.Label(self, text="Here's what's happening with your customers today.",
                 font=Fonts.BODY, bg=Colors.BG, fg=Colors.TEXT_MUTED).pack(anchor="w", pady=(0, 20))

        try:
            cust_counts = CustomerController.get_dashboard_counts()
            fu_counts = FollowUpController.get_dashboard_counts()
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
            cust_counts = {"total": 0, "active": 0, "leads": 0, "prospects": 0}
            fu_counts = {"pending": 0, "today": 0, "overdue": 0}

        cards_frame = tk.Frame(self, bg=Colors.BG)
        cards_frame.pack(fill="x", pady=(0, 25))

        cards = [
            ("Total Customers", cust_counts["total"], Colors.PRIMARY, "customers"),
            ("Pending Follow-ups", fu_counts["pending"], Colors.WARNING, "followups"),
            ("Due Today", fu_counts["today"], Colors.SUCCESS, "followups"),
            ("Overdue", fu_counts["overdue"], Colors.DANGER, "followups"),
        ]
        for i, (label, value, color, target) in enumerate(cards):
            card = self._stat_card(cards_frame, label, value, color, target)
            card.grid(row=0, column=i, padx=(0 if i == 0 else 15, 0), sticky="nsew")
            cards_frame.grid_columnconfigure(i, weight=1)

        lists_frame = tk.Frame(self, bg=Colors.BG)
        lists_frame.pack(fill="both", expand=True)
        lists_frame.grid_columnconfigure(0, weight=1)
        lists_frame.grid_columnconfigure(1, weight=1)
        lists_frame.grid_rowconfigure(0, weight=1)

        self._upcoming_followups_card(lists_frame).grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self._recent_contacts_card(lists_frame).grid(row=0, column=1, sticky="nsew", padx=(12, 0))

    def _stat_card(self, parent, label, value, color, target_page):
        card = tk.Frame(parent, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                         highlightthickness=1, cursor="hand2")
        tk.Frame(card, bg=color, height=5).pack(fill="x")
        inner = tk.Frame(card, bg=Colors.CARD, padx=18, pady=16)
        inner.pack(fill="both", expand=True)
        tk.Label(inner, text=str(value), font=Fonts.STAT_NUM, bg=Colors.CARD,
                 fg=Colors.TEXT_DARK).pack(anchor="w")
        tk.Label(inner, text=label, font=Fonts.BODY, bg=Colors.CARD,
                 fg=Colors.TEXT_MUTED).pack(anchor="w")

        def go(_e=None):
            if target_page == "customers":
                self.main_view.show_customers()
            else:
                self.main_view.show_followups()

        for widget in (card, inner):
            widget.bind("<Button-1>", go)
        for child in inner.winfo_children():
            child.bind("<Button-1>", go)
        return card

    def _upcoming_followups_card(self, parent):
        card = tk.Frame(parent, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                         highlightthickness=1)
        header = tk.Frame(card, bg=Colors.CARD, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Upcoming Follow-ups", font=Fonts.H3, bg=Colors.CARD,
                 fg=Colors.TEXT_DARK).pack(side="left")

        try:
            upcoming = FollowUpController.get_upcoming(5)
        except (ConnectionError, RuntimeError):
            upcoming = []

        body = tk.Frame(card, bg=Colors.CARD, padx=18, pady=4)
        body.pack(fill="both", expand=True)

        if not upcoming:
            tk.Label(body, text="No pending follow-ups. You're all caught up!",
                     font=Fonts.BODY, bg=Colors.CARD, fg=Colors.TEXT_MUTED).pack(pady=20)
        for f in upcoming:
            row = tk.Frame(body, bg=Colors.CARD, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=f.customer_name, font=Fonts.BODY_BOLD, bg=Colors.CARD,
                     fg=Colors.TEXT_DARK).pack(anchor="w")
            tk.Label(row, text=f"{f.purpose}  \u2022  {format_date(f.followup_date)} {format_time(f.followup_time)}",
                     font=Fonts.SMALL, bg=Colors.CARD, fg=Colors.TEXT_MUTED).pack(anchor="w")
            tk.Frame(body, bg=Colors.BORDER, height=1).pack(fill="x", pady=4)

        tk.Button(card, text="View All Follow-ups \u2192", font=Fonts.SMALL, bg=Colors.CARD,
                  fg=Colors.PRIMARY, relief="flat", bd=0, cursor="hand2",
                  command=self.main_view.show_followups).pack(anchor="w", padx=18, pady=(0, 14))
        return card

    def _recent_contacts_card(self, parent):
        card = tk.Frame(parent, bg=Colors.CARD, highlightbackground=Colors.BORDER,
                         highlightthickness=1)
        header = tk.Frame(card, bg=Colors.CARD, padx=18, pady=14)
        header.pack(fill="x")
        tk.Label(header, text="Recent Contact History", font=Fonts.H3, bg=Colors.CARD,
                 fg=Colors.TEXT_DARK).pack(side="left")

        try:
            recent = ContactHistoryController.get_recent(5)
        except (ConnectionError, RuntimeError):
            recent = []

        body = tk.Frame(card, bg=Colors.CARD, padx=18, pady=4)
        body.pack(fill="both", expand=True)

        if not recent:
            tk.Label(body, text="No contact history logged yet.",
                     font=Fonts.BODY, bg=Colors.CARD, fg=Colors.TEXT_MUTED).pack(pady=20)
        for h in recent:
            row = tk.Frame(body, bg=Colors.CARD, pady=6)
            row.pack(fill="x")
            tk.Label(row, text=f"{h.customer_name}  ({h.contact_type})", font=Fonts.BODY_BOLD,
                     bg=Colors.CARD, fg=Colors.TEXT_DARK).pack(anchor="w")
            tk.Label(row, text=f"{h.subject}  \u2022  {format_date(h.contact_date)}",
                     font=Fonts.SMALL, bg=Colors.CARD, fg=Colors.TEXT_MUTED).pack(anchor="w")
            tk.Frame(body, bg=Colors.BORDER, height=1).pack(fill="x", pady=4)

        tk.Button(card, text="View All Contact History \u2192", font=Fonts.SMALL, bg=Colors.CARD,
                  fg=Colors.PRIMARY, relief="flat", bd=0, cursor="hand2",
                  command=self.main_view.show_contacts).pack(anchor="w", padx=18, pady=(0, 14))
        return card
