# -*- coding: utf-8 -*-

"""
    dash_manager.manager.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    Dash Manager is an easy-to-use device that allows you to combine 
    multiple Dash applications on a single Flask server.
"""

from dash import Dash
from functools import wraps
from flask import Flask, abort


class BaseViewMetaClass:
    """
        View metaclass.

        Does some pre calculations to avoid
        calculating them for each view class instance.
    """
    pass

class BaseView(BaseViewMetaClass):
    """
        Base app view.

        Derive from this class to implement your interface piece.
    """
    def __init__(self, app=None, name=None, category=None, menu_icon=None, visible=True) -> None:
        """
            Constructor.

            :param app:
                Dash app or DashExpress app
            :param name:
                Name of this view. If not provided, will default to the class name.
            :param category:
                View category. If not provided, this view will be shown as a top-level menu item. Otherwise, it will
                be in a submenu.
            :param menu_icon:
                Icon name or DashIconify instance
        """
        self.init_app(app)
        self.name = name or app.config.get('name')
        self.visible = visible
        self.category = category
        self.menu_icon = menu_icon
        self.href = self.app.config.get('url_base_pathname') or '/'

    def init_app(self, app: Dash) -> None:
        if app is not None:
            self.app = app

    def is_visible(self) -> bool:
        """
            Override this method if you want dynamically hide or show app views
            from Dash Manager menu structure

            By default, item is visible in menu.

            Please note that item should be both visible and accessible to be displayed in menu.
        """
        return self.visible

    def is_accessible(self) -> bool:
        """
            Override this method to add permission checks.

            Dash Manager does not make any assumptions about the authentication system used in your application, so it is
            up to you to implement it.

            By default, it will allow access for everyone.
        """
        return True

    def embed(self, server) -> None:
        """
            Embed and secure the application on a single server
        """
        self.app.init_app(server.server)
        self.app.config['external_scripts'] += server.external_scripts or [] + server.template.add_external_scripts()
        self.app.config['external_stylesheets'] += server.external_stylesheets  or [] + server.template.add_external_stylesheets()
        server.template._app_shell(self.app)

        server._view += [self.app]
        server._views += [{'href':self.href, 
                          'name':self.name,
                          'category':self.category,
                          'menu_icon': self.menu_icon}]
        
        for view_func in server.server.view_functions:            
            if view_func.startswith(self.href):
                server.server.view_functions[view_func] = self.login_required(server.server.view_functions[view_func])

    def login_required(self, func):
        """
        If you decorate the view with this, it will ensure that access is 
        restricted in case view.is_accessible() == False
        """

        @wraps(func)
        def decorated_view(*args, **kwargs):
            if not self.is_accessible():
                return abort(401)
            return func(*args, **kwargs)

        return decorated_view


class DashManager:
    """
        Collection of the dash apps. Also manages menu structure.
    """
    pass