from functools import wraps
from flask import session, redirect, url_for, abort

def allowed_users_only(allowed_users):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = session.get('user')
            if not user:
                return redirect(url_for('login'))

            username = user.get('preferred_username')
            if username not in allowed_users:
                abort(403)  # Forbidden

            return f(*args, **kwargs)
        return decorated_function
    return decorator