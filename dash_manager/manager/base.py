# -*- coding: utf-8 -*-

"""
    dash_manager.manager.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    Dash Manager is an easy-to-use device that allows you to combine 
    multiple Dash applications on a single Flask server.
"""

import os 
import typing

from dash import Dash
from functools import wraps
from flask.ctx import AppContext
from flask import Flask, Blueprint, abort
from dash.development.base_component import Component
from .menu import MenuCategory, MenuView, MenuBluprint
from .template import BaseTemplate, BootstrapTemplate, MantineTemplate


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
            Base app view.
            Derive from this class to implement your interface piece.


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

    def inaccessible_callback(self):
        return abort(401)
    
    def embed(self, server) -> None:
        """
            Embed and secure the application on a single server
        """
        self.app.config['external_scripts'] += server.external_scripts or [] + server.template.add_external_scripts()
        self.app.config['external_stylesheets'] += server.external_stylesheets  or [] + server.template.add_external_stylesheets()
        self.app.config['title'] = self.app.config['name']
        self.app.title = f'{self.category}: {self.app.config["name"]}' if self.category else self.app.config['name']
        self.app.init_app(server.server)
        server.template._app_shell(self.app)
        
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
    def __init__(self, name:str|Component=None, server: None|Flask = None, 
                 url=None, template_mode=None,
                 category_icon=None,
                 external_scripts=None,
                external_stylesheets=None,) -> None:
        """
            The DashManager object implements a Flask application and acts as the central
            object. Once created, it will act as a central registry for 
            all Dash applications and blueprints.


            Constructor.

            :param name:
                Application name. Will be displayed in the main menu and as a page title. Defaults to "Dash Manager"
            :param server:
                Flask application object 
            :param url:
                Base URL
            :param template_mode:
                Base template path. Defaults to `mantine`. If you want to use
                Bootstrap to `bootstrap` or create custom template.
            :param category_icon:
                A dict of category names as keys and html classes as values to be added to menu category icons.
                Example: 
                ```python
                {'Airplane': html.I(className="bi bi-airplane"), 
                'Settings': DashIconify(icon="flat-ui:settings", width=22)}
                ```
            :param external_scripts: Additional JS files to load with the page.
                Each entry can be a string (the URL) or a dict with ``src`` (the URL)
                and optionally other ``<script>`` tag attributes such as ``integrity``
                and ``crossorigin``.
            :param external_stylesheets: Additional CSS files to load with the page.
                Each entry can be a string (the URL) or a dict with ``href`` (the URL)
                and optionally other ``<link>`` tag attributes such as ``rel``,
                ``integrity`` and ``crossorigin``.
        """

        self.name = name or 'Dash Manager'

        if isinstance(server, Flask):
            self.init_app(server)
        else:
            server = Flask('DashManagerServer')
            self.init_app(server)
        
        self.config = server.config
        self.base_url = url

        self._dashapps = []
        self._views = []
        self._menu = []
        self._menu_categories = dict()
        self._menu_links = []

        if isinstance(category_icon, dict):
            self.category_icon = category_icon
        else:
            self.category_icon = dict()

        self.init_template_mode(template_mode)

        self.external_stylesheets = external_stylesheets
        self.external_scripts = external_scripts

    def init_template_mode(self,template_mode):
        template_dct = {'bootstrap':BootstrapTemplate, 'mantine':MantineTemplate}
        template_mode = template_mode or 'bootstrap'
        if isinstance(template_mode, str):
            self.template = template_dct.get(template_mode, BaseTemplate)(self)
        elif isinstance(template_mode, BaseTemplate):
            self.template = template_mode(self)
        else:
            self.template = BootstrapTemplate(self)

    def logo(self):
        """Get a logo"""
        return self.name

    def add_view(self, view):
        """
            Add a view to the collection.

            :param view:
                View to add.
        """
        view.embed(self)
        # Add to views
        self._views.append(view)
        self._dashapps.append(view.app)

        if view.is_visible():
            self._add_view_to_menu(view)

    def add_views(self, *args):
        """
            Add one or more views to the collection.

            Examples::

                manger.add_views(view1)
                manger.add_views(view1, view2, view3, view4)
                manger.add_views(*my_list)

            :param args:
                Argument list including the views to add.
        """
        for view in args:
            self.add_view(view)

    def add_link(self, link:Component):
        """
            Add link to menu links collection.

            :param link:
                Link to add.
            
            Example:

            ```python
            manger.add_link(
                dmc.ActionIcon(
                    DashIconify(
                        icon='radix-icons:blending-mode', width=22
                    ),
                    variant="outline",
                    radius='md',
                    size=36,
                    color='yellow',
                    id='color-scheme-toggle',
                )
            )
            ```
        """
        self._menu_links.append(link)

    def add_links(self, *args):
        """
            Add one or more links to the menu links collection.

            Examples::

                admin.add_links(link1)
                admin.add_links(link1, link2, link3, link4)
                admin.add_links(*my_list)

            :param args:
                Argument list including the links to add.
        """
        for link in args:
            self.add_link(link)

    def register_blueprint(self, blueprint: Blueprint, name=None, category=None, menu_icon=None, visible=True, **options: typing.Any,) -> None:
        """
            Register a :class:`~flask.Blueprint` on the application. Keyword
            arguments passed to this method will override the defaults set on the
            blueprint.

            :param name:
                Name of this view. If not provided, will default to the class name.
            :param category:
                View category. If not provided, this view will be shown as a top-level menu item.
            :param menu_icon:
                Icon name or DashIconify instance
            :param visible: 
                Visible in navbar

            Calls the blueprint's :meth:`~flask.Blueprint.register` method after
            recording the blueprint in the application's :attr:`blueprints`.

            :param blueprint: The blueprint to register.
            :param url_prefix: Blueprint routes will be prefixed with this.
            :param subdomain: Blueprint routes will match on this subdomain.
            :param url_defaults: Blueprint routes will use these default values for
                view arguments.
            :param options: Additional keyword arguments are passed to
                :class:`~flask.blueprints.BlueprintSetupState`. They can be
                accessed in :meth:`~flask.Blueprint.record` callbacks.
        """
        blueprint.register(self.server, options)

        if visible:
            self.add_menu_item(MenuBluprint(name, options.get('url_prefix'), menu_icon, self), category)

    def add_menu_item(self, menu_item, target_category=None):
        """
            Add menu item to menu tree hierarchy.

            :param menu_item:
                MenuItem class instance
            :param target_category:
                Target category name
        """
        if target_category:
            category = self._menu_categories.get(target_category)

            # create a new menu category if one does not exist already
            if category is None:
                category = MenuCategory(target_category)
                category.icon = self.category_icon.get(target_category)
                self._menu_categories[target_category] = category

                self._menu.append(category)

            category.add_child(menu_item)
        else:
            self._menu.append(menu_item)

    def _add_view_to_menu(self, view):
        """
            Add a view to the menu tree

            :param view:
                View to add
        """
        self.add_menu_item(MenuView(view.name, view), view.category)      

    def init_app(self, server):
        if server is not None:
            self.server = server

    def menu(self):
        return [menu for menu in self._menu if menu._view.is_accessible()]
    
    def run(
        self,
        host=os.getenv("HOST", "127.0.0.1"),
        port=os.getenv("PORT", "8050"),
        proxy=os.getenv("DASH_PROXY", None),
        debug=False,
        dev_tools_ui=None,
        dev_tools_props_check=None,
        dev_tools_serve_dev_bundles=None,
        dev_tools_hot_reload=None,
        dev_tools_hot_reload_interval=None,
        dev_tools_hot_reload_watch_interval=None,
        dev_tools_hot_reload_max_retry=None,
        dev_tools_silence_routes_logging=None,
        dev_tools_prune_errors=None,
        **flask_run_options,
    )  -> None:
        """
            Start the flask server in local mode, you should not run this on a
            production server, use gunicorn/waitress instead.

            If a parameter can be set by an environment variable, that is listed
            too. Values provided here take precedence over environment variables.

            :param host: Host IP used to serve the application
                env: ``HOST``
            :type host: string

            :param port: Port used to serve the application
                env: ``PORT``
            :type port: int

            :param proxy: If this application will be served to a different URL
                via a proxy configured outside of Python, you can list it here
                as a string of the form ``"{input}::{output}"``, for example:
                ``"http://0.0.0.0:8050::https://my.domain.com"``
                so that the startup message will display an accurate URL.
                env: ``DASH_PROXY``
            :type proxy: string

            :param debug: Set Flask debug mode and enable dev tools.
                env: ``DASH_DEBUG``
            :type debug: bool

            :param debug: Enable/disable all the dev tools unless overridden by the
                arguments or environment variables. Default is ``True`` when
                ``enable_dev_tools`` is called directly, and ``False`` when called
                via ``run``. env: ``DASH_DEBUG``
            :type debug: bool

            :param dev_tools_ui: Show the dev tools UI. env: ``DASH_UI``
            :type dev_tools_ui: bool

            :param dev_tools_props_check: Validate the types and values of Dash
                component props. env: ``DASH_PROPS_CHECK``
            :type dev_tools_props_check: bool

            :param dev_tools_serve_dev_bundles: Serve the dev bundles. Production
                bundles do not necessarily include all the dev tools code.
                env: ``DASH_SERVE_DEV_BUNDLES``
            :type dev_tools_serve_dev_bundles: bool

            :param dev_tools_hot_reload: Activate hot reloading when app, assets,
                and component files change. env: ``DASH_HOT_RELOAD``
            :type dev_tools_hot_reload: bool

            :param dev_tools_hot_reload_interval: Interval in seconds for the
                client to request the reload hash. Default 3.
                env: ``DASH_HOT_RELOAD_INTERVAL``
            :type dev_tools_hot_reload_interval: float

            :param dev_tools_hot_reload_watch_interval: Interval in seconds for the
                server to check asset and component folders for changes.
                Default 0.5. env: ``DASH_HOT_RELOAD_WATCH_INTERVAL``
            :type dev_tools_hot_reload_watch_interval: float

            :param dev_tools_hot_reload_max_retry: Maximum number of failed reload
                hash requests before failing and displaying a pop up. Default 8.
                env: ``DASH_HOT_RELOAD_MAX_RETRY``
            :type dev_tools_hot_reload_max_retry: int

            :param dev_tools_silence_routes_logging: Silence the `werkzeug` logger,
                will remove all routes logging. Enabled with debugging by default
                because hot reload hash checks generate a lot of requests.
                env: ``DASH_SILENCE_ROUTES_LOGGING``
            :type dev_tools_silence_routes_logging: bool

            :param dev_tools_prune_errors: Reduce tracebacks to just user code,
                stripping out Flask and Dash pieces. Only available with debugging.
                `True` by default, set to `False` to see the complete traceback.
                env: ``DASH_PRUNE_ERRORS``
            :type dev_tools_prune_errors: bool

            :param flask_run_options: Given to `Flask.run`
        """

        # Verify port value
        try:
            port = int(port)
            assert port in range(1, 65536)
        except Exception as e:
            e.args = [f"Expecting an integer from 1 to 65535, found port={repr(port)}"]
            raise

        for dashapp in self._dashapps:
            
            debug = dashapp.enable_dev_tools(
                debug,
                dev_tools_ui,
                dev_tools_props_check,
                dev_tools_serve_dev_bundles,
                dev_tools_hot_reload,
                dev_tools_hot_reload_interval,
                dev_tools_hot_reload_watch_interval,
                dev_tools_hot_reload_max_retry,
                dev_tools_silence_routes_logging,
                dev_tools_prune_errors,
            )

                   
        self.server.run(host=host, port=port, debug=debug, **flask_run_options)

    def app_context(self) -> AppContext:
        """
            Create an :class:`~flask.ctx.AppContext`. Use as a ``with``
            block to push the context, which will make :data:`current_app`
            point at this application.

            ::

                with app.app_context():
                    init_db()

        """
        return self.server.app_context()
    
    def add_config(self, obj: object | str) -> None:
        """
            Updates the values from the given object.  An object can be of one
            of the following two types:

            -   a string: in this case the object with that name will be imported
            -   an actual object reference: that object is used directly

            Objects are usually either modules or classes. :meth:`from_object`
            loads only the uppercase attributes of the module/class. A ``dict``
            object will not work with :meth:`from_object` because the keys of a
            ``dict`` are not attributes of the ``dict`` class.

            Example of module-based configuration::

                manager.add_config('yourapplication.default_config')
                from yourapplication import default_config
                manager.add_config(default_config)

            Nothing is done to the object before loading. If the object is a
            class and has ``@property`` attributes, it needs to be
            instantiated before being passed to this method.

            You should not use this function to load the actual configuration but
            rather configuration defaults.  The actual config should be loaded
            with :meth:`from_pyfile` and ideally from a location not within the
            package because the package might be installed system wide.

            :param obj: an import name or object
        """
        self.server.config.from_object(obj)