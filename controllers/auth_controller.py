"""
controllers/auth_controller.py
---------------------------------
Handles the login workflow between LoginFrame and UserDAO.
"""

from dao.user_dao import UserDAO


class AuthController:

    @staticmethod
    def login(username, password):
        if not username or not username.strip():
            raise ValueError("Please enter your username.")
        if not password:
            raise ValueError("Please enter your password.")
        user = UserDAO.verify_login(username.strip(), password)
        if not user:
            raise ValueError("Invalid username or password.")
        return user
