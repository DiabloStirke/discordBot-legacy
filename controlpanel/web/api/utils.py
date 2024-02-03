from functools import wraps
from flask import request, jsonify
from web.models.authtoken import AuthToken


def token_auth(func):
    """A decorator for routes that require an auth token."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        token = request.headers.get('X-Auth-Token')
        if not token:
            return jsonify({'error': 'No auth token provided'}), 401

        token = AuthToken.get_by_token(token)
        if not token:
            return jsonify({'error': 'Invalid auth token'}), 401

        return func(*args, **kwargs)

    return wrapper
