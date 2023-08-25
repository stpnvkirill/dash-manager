# -*- coding: utf-8 -*-

"""
    dash_manager.manager.template
    ~~~~~~~~~~~~~~~~~~~~~~~

    Application implementation templates classes. You can 
    completely customize your application by overriding one 
    of the classes below
"""


import dash_bootstrap_components as dbc

from dash_iconify import DashIconify
from dash import html, Input, Output, State, dcc


class BaseTemplate(object):
    """
        Template for creating a layout with a menu structure.
    """

    def __init__(self, manager) -> None:
        """
            Constructor.

            :param manager:
                DashManager instance
        """
        self.manager = manager

    def navbar(self, menu: list):
        """
            Override this method to create a custom navigation bar

            Menu is list of dash_manager.manager.menu.MenuView or 
            dash_manager.manager.menu.MenuCategory object
        """
        return html.Header(
            [html.Div(self.manager.logo())]
            +
            [html.Nav(
                html.Ul(
                    [html.Li(
                        html.A(menu_item.name, href=menu_item.get_url())
                    )
                    if not menu_item.is_category() else
                    html.Li([menu_item.name, html.Ul([html.Li(html.A(
                        subitem.name, href=subitem.get_url())) for subitem in menu_item.get_children()])])
                    for menu_item in menu]
                ))])

    def app_container(self, navbar, app_layout, footer):
        """
            Override this method to create a custom container
        """
        return html.Main([navbar, app_layout, footer])

    def footer(self):
        """
            Override this method to create a custom footer
        """
        return html.Footer()

    def add_callbacks(self, dash_app):
        """
            Override this method to add callbacks
        """
        pass

    def add_external_scripts(self):
        """
            Override this method to add external_scripts
        """
        return []

    def add_external_stylesheets(self):
        """
            Override this method to add external_stylesheets
        """
        return []

    def _layout(self, dash_app):
        server = self.manager.server
        layout = dash_app.layout
        layout = layout() if callable(layout) else layout
        menu_structure = self.manager.menu()

        def shell():
            with server.app_context():
                res = self.app_container(self.navbar(
                    menu_structure), layout, self.footer())
                return res

        return shell

    def _app_shell(self, dash_app):
        self.add_callbacks(dash_app)
        dash_app.layout = self._layout(dash_app=dash_app)

class BootstrapTemplate(BaseTemplate):
    def navbar(self, menu: list):
        nav = [
            dbc.NavbarBrand(self.manager.logo()),
            dbc.Nav(
                [
                    dbc.NavItem(dbc.NavLink(menu_item.name,
                                            href=menu_item.get_url(), external_link=True))
                    if not menu_item.is_category() else
                    dbc.DropdownMenu(
                        children=[dbc.DropdownMenuItem(subitem.name, href=subitem.get_url(
                        ), external_link=True) for subitem in menu_item.get_children()],
                        label=menu_item.name,
                        nav=True,

                    )
                    for menu_item in menu
                ])
        ]

        return dbc.Navbar(
            dbc.Container(
                [
                    dbc.NavbarToggler(id="navbar-toggler", n_clicks=0),
                    dbc.Collapse(
                        nav,
                        id="navbar-collapse",
                        is_open=False,
                        navbar=True,
                    ),
                    html.Div(className="d-flex align-items-center",
                             children=dbc.Button(DashIconify(icon='radix-icons:blending-mode', height=25), 
                                                 color='secondary', id="color-scheme-toggle"), n_clicks=0)
                ]
            ),
            color='secondary',
            dark=True
        )

    def app_container(self, navbar, app_layout, footer):
        return html.Main([navbar, 
                          dbc.Container(app_layout, style={'margin-top': '15px'}),
                          footer,
                          dcc.Store(id="theme-store", storage_type="local"),])

    def add_callbacks(self, dash_app):
        # add callback for toggling the collapse on small screens
        dash_app.clientside_callback(
            """function(n_clicks, is_open) { 
                const open = is_open ? false : true
                if (n_clicks) {return open}
                else { return dash_clientside.no_update }
            }""",
            Output("navbar-collapse", "is_open"),
            [Input("navbar-toggler", "n_clicks")],
            [State("navbar-collapse", "is_open")],
        )
  
        dash_app.clientside_callback(
            """function(n_clicks, data) {
                if (data) {
                    if (n_clicks) {
                        const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                        document.querySelector("body").setAttribute('data-bs-theme', scheme)
                        return { colorScheme: scheme } 
                    }
                    document.querySelector("body").setAttribute('data-bs-theme', data["colorScheme"])
                    return dash_clientside.no_update
                } else {
                    document.querySelector("body").setAttribute('data-bs-theme', "light")
                    return { colorScheme: "light" }
                }
            }""",
            Output("theme-store", "data"),
            Input("color-scheme-toggle", "n_clicks"),
            State("theme-store", "data"),
        )
        
        return super().add_callbacks(dash_app)

    def add_external_stylesheets(self):
        return [dbc.themes.BOOTSTRAP]

class MantineTemplate(BaseTemplate):
    pass

