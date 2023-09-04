# Customize your application

If the built-in themes don't work for you, you can override the dash_manager.manager.template.BaseTemplate class.


```python
class MyTemplate(BaseTemplate):
    def navbar(self, menu: list, links: list):
        """
            Override this method to create a custom navigation bar

            Menu is list of dash_manager.manager.menu.MenuView or 
            dash_manager.manager.menu.MenuCategory object
        """
        ...

    def app_container(self, navbar, app_layout, footer):
        """
            Override this method to create a custom container
        """
        ...

    def footer(self):
        """
            Override this method to create a custom footer
        """
        ...

```

The core of the template is the 3 methods by which the navigation bar, the application 
container and the footer are defined. Each method must return a Dash component. Here is 
an example of a basic implementation.


```python
class BootstrapTemplate(BaseTemplate):
    FLUID = False


    def add_external_stylesheets(self):
        # To avoid adding bootstrap css in every application we will do it 
        # with a template. If you use your own css in the assets folder, 
        # override the add_external_stylesheets method so that it returns an empty list
        return [dbc.themes.BOOTSTRAP]
    
    # In addition to css, you can add js using the add_external_scripts method

    def add_links(self):
        # Add a button for a dark theme
        return [dbc.Button(DashIconify(icon='radix-icons:blending-mode', height=25),
                           color='secondary', id="color-scheme-toggle", n_clicks=0)]

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

        # add callback to change the theme
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

    def navbar(self, menu: list, links: list):
        # Create a navbar as described in the documentation: 
        # https://dash-bootstrap-components.opensource.faculty.ai/docs/components/navbar/

        # The menu buttons and links remain the key here,
        # Menu is list of dash_manager.manager.menu.MenuView or        
        # dash_manager.manager.menu.menu.MenuCategory object.
        # Below is a simple example of how to implement a menu.

        # Links represent a list of already ready Dash compnonets, 
        # so you just need to place them in the right place in the layout.

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
        # Let's put the source layout in a bootstrap container, and 
        # add a Store to store the selected theme
        return html.Main([navbar,
                          dbc.Container(app_layout, style={
                                        'margin-top': '15px'}, fluid=self.FLUID),
                          footer,
                          dcc.Store(id="theme-store", storage_type="local"),])
```

By overriding the basic template you can easily fully customize your application