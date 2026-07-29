"""
main.py
--------
CRM Pro - Entry point.

Run this file to start the application:
    python main.py

Architecture note: the whole application uses exactly ONE persistent
tk.Tk() root window (this class). The Login screen and the Main app
shell are both plain tk.Frame objects that get swapped in and out of
this single root - this avoids the classic Tkinter bugs that come
from creating multiple Tk() instances or nesting mainloop() calls.
"""

import tkinter as tk
from tkinter import messagebox

from views.styles import apply_global_style, Colors
from views.login_view import LoginFrame
from views.main_view import MainFrame


class CRMApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CRM Pro - Customer Relationship Management")
        self.configure(bg=Colors.BG)
        self.minsize(360, 480)
        apply_global_style()

        self.current_frame = None
        self.show_login()

    def show_login(self):
        self._clear_current_frame()
        self.resizable(False, False)
        self._center(420, 520)
        self.current_frame = LoginFrame(self, on_success=self.show_main)
        self.current_frame.pack(fill="both", expand=True)

    def show_main(self, user):
        self._clear_current_frame()
        self.resizable(True, True)
        self._maximize()
        self.current_frame = MainFrame(self, user, on_logout=self.show_login)
        self.current_frame.pack(fill="both", expand=True)
        # F11 toggles TRUE fullscreen (hides the title bar too, like a browser).
        # Esc always exits back to the normal maximized window.
        self.bind("<F11>", self._toggle_fullscreen)
        self.bind("<Escape>", self._exit_fullscreen)

    def _maximize(self):
        """Reliably fill the screen on Windows, Linux, and Mac.

        Some window managers accept `state("zoomed")` without raising an
        error but then silently do nothing (no WM listening to honor the
        request). So instead of trusting that call alone, we ALWAYS set
        an explicit full-screen geometry as a guaranteed baseline first,
        then layer the native "maximized" state on top as a bonus - it
        gives the proper OS maximize/restore behavior when supported,
        but the window fills the screen either way even if it isn't."""
        self.update_idletasks()
        w, h = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"{w}x{h}+0+0")
        try:
            self.state("zoomed")               # Windows, and some Linux window managers
        except tk.TclError:
            try:
                self.attributes("-zoomed", True)   # most other Linux window managers
            except tk.TclError:
                pass  # explicit geometry above already fills the screen

    def _toggle_fullscreen(self, _event=None):
        is_full = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not is_full)

    def _exit_fullscreen(self, _event=None):
        self.attributes("-fullscreen", False)

    def _clear_current_frame(self):
        if self.current_frame is not None:
            self.current_frame.destroy()
            self.current_frame = None

    def _center(self, width, height):
        self.update_idletasks()
        x = (self.winfo_screenwidth() - width) // 2
        y = (self.winfo_screenheight() - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")


def main():
    try:
        app = CRMApp()
        app.mainloop()
    except Exception as e:
        # Last-resort safety net so the user always gets a readable
        # message instead of a raw traceback / silent crash.
        try:
            messagebox.showerror("Fatal Error", f"The application could not start.\n\n{e}")
        except tk.TclError:
            print(f"Fatal Error: {e}")


if __name__ == "__main__":
    main()
