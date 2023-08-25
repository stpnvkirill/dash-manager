# Dash Manager

Dash Manager is an easy-to-use device that allows you to combine multiple Dash applications on a single Flask server.

## Simple Example

```python
from dash_manager import DashManager, BaseView
from dash import Dash,html


manager = DashManager()


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