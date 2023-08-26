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