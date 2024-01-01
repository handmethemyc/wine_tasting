from functools import wraps
from flask import session, redirect, url_for


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("wine.index"))  # Redirect to the login page
        return func(*args, **kwargs)

    return decorated_view
