# Dash Manager

Dash Manager is an easy-to-use device that allows you to combine multiple Dash applications on a single Flask server. 
A layout wrapper is also adding for each application into which common elements, such as the navigation bar, can be encoded.

## Simple Example

```python
from dash_manager import DashManager, BaseView
from dash import Dash, html


manager = DashManager(template_mode='bootstrap') # or mantine


# Pages
page = Dash(name='First Dashboard')
page.layout = lambda: html.Div('This is First Dashboard')

page2 = Dash(name='Second Dashboard', url_base_pathname='/two/')
page2.layout = lambda: html.Div('This is Second Dashboard')

page3 = Dash(name='Third Dashboard', url_base_pathname='/three/')
page3.layout = lambda: html.Div('This is Third Dashboard')


# Views
manager.add_view(BaseView(page, category='Dropdown'))
manager.add_view(BaseView(page2, category='Dropdown'))
manager.add_view(BaseView(page3))

# Run app
manager.run(debug=True)
```


## Instalation

Dash-manager is published as a Python package and can be installed with pip, ideally by using a virtual environment. 
Open up a terminal and install dash-manager with:

```bash
pip install dash-manager
```

This will automatically install compatible versions of all dependencies: Flask, Dash, Dash Bootstrap & Dash Mantine. 
Dash manager always strives to support the latest versions, so there's no need to install those packages separately.


## Creating your app

After you've installed Dash Manager, you can create a recommended application structure. Go to the directory where you want 
your project to be located and enter:

```bash
dash_manager new *
```

This will create the following structure, where in each file there will be detailed descriptions:

```
.
├─ assets/
├─ webApp/
│  └─ views
│     └─ first_dash
│        └─ __init__.py
│        └─ app.py
│     └─ second_dash
│        └─ __init__.py
│        └─ app.py
│     └─ __init__.py
│  └─ __init__.py
│  └─ config.py
│  └─ server.py
└─ wsgi.py
```

The resulting project is a basic application that can be run via wsgi.py:

```bash
python wsgi.py
```

## Protecting

Dash Manager lets you define access control rules on each of your view classes by simply 
overriding the is_accessible method. How you implement the logic is up to you, but if you were 
to use a low-level library like Flask-Login, then restricting access could be as simple as:

```python
from dash_manager import BaseView
from flask import redirect, url_for
from flask_login import current_user


class MyView(BaseView):

    def is_accessible(self):
        return current_user and current_user.is_authenticated

    def inaccessible_callback(self, name, **kwargs):
        # redirect to login page if user doesn't have access
        return redirect(url_for('login', next=request.url))
```


In the navigation menu, components that are not accessible to a particular user will not be 
displayed for that user. The main drawback is that you still need to implement all of the 
relevant login, registration, and account management views yourself.


## Customization

You can use two built-in themes for your application: Bootstrap & Mantine. But if you need a 
completely custom interface: override dash_manager.manager.template.BaseTemplate class.


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

Read more about this here
