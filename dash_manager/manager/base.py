# -*- coding: utf-8 -*-

"""
    dash_manager.manager.base
    ~~~~~~~~~~~~~~~~~~~~~~~

    Dash Manager is an easy-to-use device that allows you to combine 
    multiple Dash applications on a single Flask server.
"""


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
    pass

class DashManager:
    """
        Collection of the dash apps. Also manages menu structure.
    """
    pass