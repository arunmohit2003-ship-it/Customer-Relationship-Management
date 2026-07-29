"""
views/login_view.py
---------------------
Login screen. This is a tk.Frame (NOT its own Tk window) so it can be
swapped in and out of the single persistent root window created in
main.py, without ever creating a second Tk() instance.
"""

import tkinter as tk
from tkinter import messagebox

from controllers.auth_controller import AuthController
from views.styles import Colors, Fonts, make_button


class LoginFrame(tk.Frame):
    def __init__(self, parent, on_success):
        super().__init__(parent, bg=Colors.BG)
        self.on_success = on_success
        self.pack(fill="both", expand=True)
        self._build_ui()

    def _build_ui(self):
        card = tk.Frame(self, bg=Colors.WHITE, padx=40, pady=40)
        card.place(relx=0.5, rely=0.5, anchor="center", width=360, height=430)

        tk.Label(card, text="CRM PRO", font=("Segoe UI", 24, "bold"),
                 bg=Colors.WHITE, fg=Colors.PRIMARY).pack(pady=(0, 4))
        tk.Label(card, text="Customer Relationship Management",
                 font=Fonts.SMALL, bg=Colors.WHITE, fg=Colors.TEXT_MUTED).pack(pady=(0, 30))

        tk.Label(card, text="Username", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x")
        self.username_entry = tk.Entry(card, font=Fonts.BODY, relief="solid", bd=1)
        self.username_entry.pack(fill="x", ipady=6, pady=(4, 16))
        self.username_entry.insert(0, "admin")

        tk.Label(card, text="Password", font=Fonts.BODY_BOLD, bg=Colors.WHITE,
                 fg=Colors.TEXT_DARK, anchor="w").pack(fill="x")
        self.password_entry = tk.Entry(card, font=Fonts.BODY, relief="solid", bd=1, show="*")
        self.password_entry.pack(fill="x", ipady=6, pady=(4, 24))

        login_btn = make_button(card, "Login", self._attempt_login, width=20)
        login_btn.pack(fill="x", ipady=4)

        tk.Label(card, text="Default: admin / admin123", font=Fonts.SMALL,
                 bg=Colors.WHITE, fg=Colors.TEXT_MUTED).pack(pady=(16, 0))

        self.username_entry.bind("<Return>", lambda e: self.password_entry.focus_set())
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())
        self.username_entry.focus_set()

    def _attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get()
        try:
            user = AuthController.login(username, password)
            self.on_success(user)
        except ValueError as e:
            messagebox.showerror("Login Failed", str(e))
        except (ConnectionError, RuntimeError) as e:
            messagebox.showerror("Database Error", str(e))
