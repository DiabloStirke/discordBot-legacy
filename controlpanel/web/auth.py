from typing import Any, Callable
from functools import wraps
from inspect import getfullargspec
from flask import session, redirect, url_for, render_template, request, jsonify
from flask.sansio.scaffold import T_route
from flask.blueprints import Blueprint
from web.models.user import RoleEnum, User
from web.models.authtoken import AuthToken
from web.utils import tz_now, get_main_context


class AuthBlueprint(Blueprint):
    def auth_route(
        self,
        rule: str,
        require_auth: bool = False,
        required_role: RoleEnum = None,
        **options: Any
    ) -> Callable[[T_route], T_route]:
        """Decorate a view function to register it with the given URL
        rule and options. Check if the user is authenticated and has the given role.
        Calls :meth:`add_url_rule`, which has more details about the implementation.
        Can pass the user object to the view function if it's in the arguments.

        .. code-block:: python

            @blueprint.route("/")
            def index(user: User):
                # user is passed to the view function!
                return "Hello, World!"

        See :ref:`url-route-registrations`.

        The endpoint name for the route defaults to the name of the view
        function if the ``endpoint`` parameter isn't passed.

        The ``methods`` parameter defaults to ``["GET"]``. ``HEAD`` and
        ``OPTIONS`` are added automatically.

        :param rule: The URL rule string.
        :param options: Extra options passed to the
            :class:`~werkzeug.routing.Rule` object.
        """
        def decorator(func: T_route) -> T_route:
            if not options.get('endpoint'):
                options['endpoint'] = func.__name__
            pass_user = 'user' in getfullargspec(func).args
            if required_role:
                func = self._ensure_role(func, required_role)
            if require_auth or required_role:
                func = self._ensure_session(func, pass_user=pass_user)
            return self.route(rule, **options)(func)
        return decorator

    def token_route(self, rule: str, **options: Any) -> Callable[[Callable], Callable]:
        """Decorate a view function to register it with the given URL
        rule and options. Checks for token authentication.
        Calls :meth:`add_url_rule`, which has more
        details about the implementation.

        .. code-block:: python

            @app.route("/")
            def index():
                return "Hello, World!"

        See :ref:`url-route-registrations`.

        The endpoint name for the route defaults to the name of the view
        function if the ``endpoint`` parameter isn't passed.

        The ``methods`` parameter defaults to ``["GET"]``. ``HEAD`` and
        ``OPTIONS`` are added automatically.

        :param rule: The URL rule string.
        :param options: Extra options passed to the
            :class:`~werkzeug.routing.Rule` object.
        """

        def decorator(func):
            if not options.get('endpoint'):
                options['endpoint'] = func.__name__
            func = self._ensure_token(func)
            return self.route(rule, **options)(func)
        return decorator

    def _ensure_session(self, func: T_route, pass_user=False) -> T_route:
        """Ensure the user has a valid session. If not, redirect to the login page"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            path_params = {}
            if request.endpoint not in ['auth.login', 'auth.index']:
                path_params['next'] = request.path
            if 'token' not in session or 'expires' not in session:
                return redirect(url_for('auth.login', **path_params))
            if session['expires'] < tz_now():
                path_params['refresh'] = True
                redirect(url_for('auth.login', **path_params))
            if pass_user:
                args = User.get_by_id(session['user']['id']), *args
            return func(*args, **kwargs)
        return wrapper

    def _ensure_role(self, func: T_route, role: RoleEnum) -> T_route:
        """Ensure the user has the required role. If not, return a 403"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = User.get_by_id(session['user']['id'])
            if not user or user.role < role:
                return render_template('forbidden.html', **get_main_context()), 403
            return func(*args, **kwargs)
        return wrapper

    def _ensure_token(self, func: T_route) -> T_route:
        """Ensure the user has a valid session. If not, redirect to the login page"""
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
