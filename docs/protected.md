# Protect your application

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


If you don't want to fully code the authorization logic yourself, you can use the built-in 
authorization application template. Go to the directory where you want your project to be 
located and enter:

<div class="termy">

```console
$ dash-manager protected_new *
```

</div>


This will create the following structure, where in each file there will be detailed descriptions:

```
.
├─ assets/
├─ webApp/
│  └─ views
│     └─ auth
│        └─ __init__.py
│        └─ admin.py
│        └─ app.py
│     └─ first_dash
│        └─ __init__.py
│        └─ app.py
│     └─ second_dash
│        └─ __init__.py
│        └─ app.py
│     └─ __init__.py
│  └─ __init__.py
│  └─ config.py
│  └─ models.py
│  └─ server.py
└─ wsgi.py
```

The resulting project is a basic application that can be run via wsgi.py:

<div class="termy">

```console
$ python wsgi.py
```

</div>