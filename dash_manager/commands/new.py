from __future__ import annotations

import logging
import os


wsgi_text = """# -*- coding: utf-8 -*-

from webApp import create_app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)"""
webapp_init_text = """# -*- coding: utf-8 -*-

from .server import create_app"""
webapp_config_text = """# -*- coding: utf-8 -*-

'''
Applications need some kind of configuration. There are different settings 
you might want to change depending on the application environment like toggling 
the debug mode, setting the secret key, and other such environment-specific things.
'''


class Config:
    SECRET_KEY = 'the random string'"""
webapp_server_text = """# -*- coding: utf-8 -*-

'''
The application factory is a function return a configured instance of a 
Flask application, instead of instantiating one in the global scope. 
Traditionally the function is (very creatively) named create_app
'''

from dash_manager import DashManager


# Declare the desired extensions (SQLAlchemy, Flask-Login, Flask-Mail...)
# Example: db = SQLAlchemy()


def create_app():

    manager = DashManager(template_mode='bootstrap')

    # Configuration
    from .config import Config
    manager.add_config(Config)


    # Initialize the application in extensions
    # Example: db.init_app(manager.server)


    # Add dash apps
    from .views import create_first_dash, create_second_dash

    manager.add_view(create_first_dash())
    manager.add_view(create_second_dash())


    # More about the factory:
    # https://flask.palletsprojects.com/en/2.3.x/patterns/appfactories/

    return manager"""
views_init_text = """# -*- coding: utf-8 -*-

from .second_dash import create_second_dash
from .first_dash import create_first_dash"""
first_dash_init_text = """# -*- coding: utf-8 -*-

from .app import create_first_dash"""
first_dash_app_text = """# -*- coding: utf-8 -*-

from dash import Dash, html
from dash_manager import BaseView


def create_first_dash():
    app = Dash(name='First Dashboard')
    app.layout = lambda: html.Div('This is First Dashboard')

    return BaseView(app)"""
second_dash_init_text = """# -*- coding: utf-8 -*-

from .app import create_second_dash"""
second_dash_app_text = """# -*- coding: utf-8 -*-

from dash import Dash, html
from dash_manager import BaseView


def create_second_dash():
    app = Dash(name='Second Dashboard', url_base_pathname='/two/')
    app.layout = lambda: html.Div('This is Second Dashboard')

    return BaseView(app)"""

log = logging.getLogger(__name__)


def new(output_dir: str) -> None:
    assets_dir = os.path.join(output_dir, 'assets')
    webApp_dir = os.path.join(output_dir, 'webApp')    
    views_dir = os.path.join(webApp_dir, 'views')
    first_dash_dir = os.path.join(views_dir, 'first_dash')
    second_dash_dir = os.path.join(views_dir, 'second_dash')

    if os.path.exists(webApp_dir):
        log.info('Project already exists.')
        return

    if not os.path.exists(output_dir):
        log.info(f'Creating project directory: {output_dir}')
        os.mkdir(output_dir)

    # Create directory
    for drt in [assets_dir, webApp_dir, views_dir, first_dash_dir, second_dash_dir]:
        log.info(f'Writing: {drt}')
        if not os.path.exists(drt):
            os.mkdir(drt)


    # Create files
    files = {
        os.path.join(output_dir, 'wsgi.py'):wsgi_text,
        os.path.join(webApp_dir, '__init__.py'): webapp_init_text,
        os.path.join(webApp_dir, 'config.py'): webapp_config_text,
        os.path.join(webApp_dir, 'server.py'): webapp_server_text,
        os.path.join(views_dir, '__init__.py'): views_init_text,
        os.path.join(first_dash_dir, '__init__.py'): first_dash_init_text,
        os.path.join(first_dash_dir, 'app.py'): first_dash_app_text,
        os.path.join(second_dash_dir, '__init__.py'): second_dash_init_text,
        os.path.join(second_dash_dir, 'app.py'): second_dash_app_text,
    }

    for pth, text in files.items(): 
        log.info(f'Writing: {pth}')
        with open(pth, 'w', encoding='utf-8') as f:
            f.write(text)
