# -*- coding: utf-8 -*-

"""
    dash_manager.manager.template
    ~~~~~~~~~~~~~~~~~~~~~~~

    Application implementation templates classes. You can 
    completely customize your application by overriding one 
    of the classes below
"""

import copy

import dash_bootstrap_components as dbc
import dash_mantine_components as dmc

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

        manager.add_links(*self.add_links())

    def navbar(self, menu: list, links: list):
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

    def add_links(self):
        """
            Override this method to add links to menu links collection.
        """
        return []

    def _layout(self, dash_app):

        layout = dash_app.layout        

        def shell():
            l = layout() if callable(layout) else layout
            menu_structure = self.manager.menu()
            links = self.manager._menu_links
            res = self.app_container(self.navbar(
                menu_structure, links), l, self.footer())
            return res

        return shell

    def _app_shell(self, dash_app):
        self.add_callbacks(dash_app)
        dash_app.layout = self._layout(dash_app=dash_app)


class BootstrapTemplate(BaseTemplate):
    FLUID = False

    def add_links(self):
        return [dbc.Button(DashIconify(icon='radix-icons:blending-mode', height=25),
                           color='secondary', id="color-scheme-toggle", n_clicks=0)]

    def navbar(self, menu: list, links: list):
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
                             children=links)
                ],
                fluid=self.FLUID
            ),
            color='secondary',
            dark=True
        )

    def app_container(self, navbar, app_layout, footer):
        return html.Main([navbar,
                          dbc.Container(app_layout, style={
                                        'margin-top': '15px'}, fluid=self.FLUID),
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
    THEME = {}
    CONTAINER_SIZE = 'xxl'

    def add_links(self):
        return [dmc.ActionIcon(
            DashIconify(
                icon='radix-icons:blending-mode', width=22
            ),
            variant="outline",
            radius='md',
            size=36,
            color='yellow',
            id='color-scheme-toggle',
        )]

    def nav_link(self, menu_item):
        if menu_item.is_category():
            return dmc.Menu(
                [
                    dmc.MenuTarget(
                        dmc.Button(menu_item.name,
                                   rightIcon=DashIconify(
                                       icon='radix-icons:chevron-down'),
                                   leftIcon=menu_item.icon,
                                   variant='subtle'
                                   )),
                    dmc.MenuDropdown(
                        [
                            dmc.MenuItem(
                                menu_i.name,
                                href=menu_i.get_url(),
                                refresh=True,
                                icon=menu_i.icon,
                            )
                            for menu_i in menu_item.get_children()
                        ]
                    ),
                ],
                transition="rotate-right",
                transitionDuration=150,
            )
        return dmc.Anchor(
            dmc.Button(
                menu_item.name,
                variant='subtle',
                leftIcon=menu_item.icon),
            href=menu_item.get_url(), refresh=True
        )

    def logo(self):
        if isinstance(self.manager.logo(), str):
            return html.Div([dmc.MediaQuery(
                dmc.Anchor(
                    self.manager.logo(),
                    size="xl",
                    href="/",
                    underline=False,
                ),
                smallerThan="lg",
                styles={"display": "none"},
            ),
                dmc.MediaQuery(
                dmc.Anchor(
                    ''.join([n[0]
                            for n in self.manager.logo().split()]).upper(),
                    size="xl",
                    href="/",
                    underline=False,
                ),
                largerThan="lg",
                styles={"display": "none"},
            )])
        return self.manager.logo()

    def mobile_link(self, link):
        try:
            link = copy.deepcopy(link)
            if link.id:
                link.id += '-dropdown'

            return link
        except:
            return link

    def navbar(self, menu: list, links: list):
        nav_cont = dmc.Grid(
            children=[
                dmc.Col(
                    dmc.Group(
                        position="left",
                        spacing="md",
                        children=[
                            dmc.Text(self.logo()),
                            dmc.MediaQuery(
                                dmc.Group([self.nav_link(menu_item)
                                          for menu_item in menu], spacing=3),
                                smallerThan="lg",
                                styles={"display": "none"}, )

                        ]),
                    span="content",
                    pt=12,
                ),
                dmc.Col(
                    span="auto",
                    children=dmc.Group(
                        position="right",
                        spacing="md",
                        children=[dmc.MediaQuery(
                            link,
                            smallerThan="lg",
                            styles={"display": "none"},)
                         for link in links] +
                        [
                            dmc.MediaQuery(
                                dmc.Menu(
                                    [
                                        dmc.MenuTarget(
                                            dmc.ActionIcon(
                                                DashIconify(
                                                    icon="line-md:close-to-menu-alt-transition",
                                                    width=18,
                                                ),
                                                variant="outline",
                                                radius='sm',
                                                size='lg',
                                            )),
                                        dmc.MenuDropdown(
                                            sum([
                                                sum([[dmc.MenuLabel(
                                                    menu_item.name, miw=200, py=5)],
                                                    [
                                                        dmc.MenuItem(
                                                            child.name,
                                                            icon=DashIconify(icon='radix-icons:chevron-right'), href=child.get_url(),
                                                            py=5, refresh=True
                                                        )
                                                        for child in menu_item.get_children()
                                                ]], []) if menu_item.is_category() else
                                                [dmc.MenuLabel(
                                                    menu_item.name, miw=200, py=5), dmc.MenuItem(
                                                    menu_item.name,
                                                    icon=DashIconify(icon='radix-icons:chevron-right'), href=menu_item.get_url(),
                                                    py=5, refresh=True
                                                )]
                                                for menu_item in menu
                                            ], [])
                                            +
                                            [
                                                dmc.MenuDivider(),
                                                dmc.SimpleGrid(
                                                    [
                                                        self.mobile_link(link) for link in links
                                                    ], cols=4, my=10)],
                                            miw=200,
                                            style={'z-index': '30000'}
                                        )
                                    ],
                                    position="bottom-end",
                                    offset=5
                                ),
                                largerThan="lg",
                                styles={"display": "none"},
                            ),
                        ]),
                ),
            ],
        )

        navbar = dmc.Header(
            height=60,
            px=0,
            mb=15,
            withBorder=True,
            children=[
                dmc.Stack(
                    justify="center",
                    style={"height": 60},
                    children=nav_cont)
            ],
        )

        return navbar

    def app_container(self, navbar, layout, footer):
        return dmc.MantineProvider(
            dmc.MantineProvider(
                theme=self.THEME,
                inherit=True,
                children=[
                    dcc.Store(id="theme-store", storage_type="local"),
                    dcc.Location(id="url"),
                    dmc.Container(
                        [
                            navbar,
                            layout,
                            footer
                        ], size=self.CONTAINER_SIZE)
                ]
            ),
            theme={"colorScheme": 'indigo'},
            id="mantine-docs-theme-provider",
            withGlobalStyles=True,
            withNormalizeCSS=True,
        )

    def add_callbacks(self, dash_app):
        dash_app.clientside_callback(
            """ function(data) { return data } """,
            Output("mantine-docs-theme-provider", "theme"),
            Input("theme-store", "data"),
        )

        dash_app.clientside_callback(
            """function(n_clicks,n_clicks2, data) {
                if (data) {
                    if (n_clicks || n_clicks2) {
                        const scheme = data["colorScheme"] == "dark" ? "light" : "dark"
                        return { colorScheme: scheme } 
                    }
                    return dash_clientside.no_update
                } else {
                    return { colorScheme: "light" }
                }
            }""",
            Output("theme-store", "data"),
            Input("color-scheme-toggle", "n_clicks"),
            Input("color-scheme-toggle-dropdown", "n_clicks"),
            State("theme-store", "data"),
        )
