"""
views/styles.py
-----------------
Single source of truth for colors, fonts, and shared ttk styling.
Every view imports Colors / Fonts from here so the whole app looks
like ONE consistent, professionally designed product instead of a
patchwork of screens.
"""

import tkinter as tk
from tkinter import ttk


class Colors:
    SIDEBAR        = "#1B2A4A"
    SIDEBAR_HOVER  = "#2C3E63"
    SIDEBAR_ACTIVE = "#4A90D9"
    BG             = "#F3F5F9"
    CARD           = "#FFFFFF"
    BORDER         = "#E1E5EC"
    TEXT_DARK      = "#22303F"
    TEXT_MUTED     = "#7A8699"
    PRIMARY        = "#2F6FE4"
    PRIMARY_DARK   = "#2559BE"
    SUCCESS        = "#27AE60"
    WARNING        = "#F2994A"
    DANGER         = "#EB5757"
    WHITE          = "#FFFFFF"


class Fonts:
    TITLE     = ("Segoe UI", 22, "bold")
    H2        = ("Segoe UI", 15, "bold")
    H3        = ("Segoe UI", 12, "bold")
    BODY      = ("Segoe UI", 10)
    BODY_BOLD = ("Segoe UI", 10, "bold")
    SMALL     = ("Segoe UI", 9)
    SIDEBAR   = ("Segoe UI", 11)
    STAT_NUM  = ("Segoe UI", 26, "bold")


def apply_global_style():
    """Configure ttk styles used across the whole app. Call once at startup."""
    style = ttk.Style()
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass  # fall back to whatever default theme is available

    style.configure("Treeview",
                     background=Colors.WHITE,
                     fieldbackground=Colors.WHITE,
                     foreground=Colors.TEXT_DARK,
                     rowheight=30,
                     font=Fonts.BODY,
                     borderwidth=0)
    style.configure("Treeview.Heading",
                     background=Colors.SIDEBAR,
                     foreground=Colors.WHITE,
                     font=Fonts.BODY_BOLD,
                     relief="flat")
    style.map("Treeview.Heading", background=[("active", Colors.PRIMARY_DARK)])
    style.map("Treeview", background=[("selected", Colors.PRIMARY)],
              foreground=[("selected", Colors.WHITE)])

    style.configure("TCombobox", font=Fonts.BODY)
    style.configure("TNotebook", background=Colors.BG, borderwidth=0)
    style.configure("TNotebook.Tab", font=Fonts.BODY_BOLD, padding=(14, 8))

    return style


def _darken(hex_color: str, factor: float = 0.85) -> str:
    """Return a slightly darker shade of a #RRGGBB color, for hover states."""
    hex_color = hex_color.lstrip("#")
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (max(0, int(c * factor)) for c in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


def make_button(parent, text, command, bg=None, fg=None,
                 hover_bg=None, font=None, width=None, padx=16, pady=8):
    """Factory for a consistent, hover-aware flat button used everywhere."""
    bg = bg or Colors.PRIMARY
    fg = fg or Colors.WHITE
    font = font or Fonts.BODY_BOLD
    hover_bg = hover_bg or _darken(bg)

    btn = tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
                     activebackground=hover_bg, activeforeground=fg,
                     font=font, relief="flat", cursor="hand2",
                     bd=0, padx=padx, pady=pady)
    if width:
        btn.config(width=width)

    def on_enter(_e):
        btn["bg"] = hover_bg

    def on_leave(_e):
        btn["bg"] = bg

    btn.bind("<Enter>", on_enter)
    btn.bind("<Leave>", on_leave)
    return btn


def status_color(status: str) -> str:
    return {
        "Pending": Colors.WARNING,
        "Completed": Colors.SUCCESS,
        "Cancelled": Colors.DANGER,
        "Rescheduled": Colors.PRIMARY,
        "Active": Colors.SUCCESS,
        "Lead": Colors.WARNING,
        "Prospect": Colors.PRIMARY,
        "Inactive": Colors.TEXT_MUTED,
        "Positive": Colors.SUCCESS,
        "Negative": Colors.DANGER,
        "Neutral": Colors.WARNING,
        "No Response": Colors.TEXT_MUTED,
    }.get(status, Colors.TEXT_MUTED)
