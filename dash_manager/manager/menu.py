# -*- coding: utf-8 -*-

"""
    dash_manager.manager.menu
    ~~~~~~~~~~~~~~~~~~~~~~~

    The logic of registering and creating menu items
"""


class BaseMenu(object):
    """
        Base menu item
    """

    def __init__(self, name, icon=None, icon_category=None, manager=None):
        self.name = name
        self.icon = icon
        self.icon_category = icon_category
        self.manager = manager

        self.parent = None
        self._children = []

    def add_child(self, menu):
        menu.parent = self
        self._children.append(menu)

    def get_url(self):
        raise NotImplementedError()

    def is_category(self):
        return False

    def get_children(self):
        return [c for c in self._children]

class MenuCategory(BaseMenu):
    """
        Menu category item.
    """

    def get_url(self):
        return None

    def is_category(self):
        return True

class MenuView(BaseMenu):
    """
        App view menu item
    """

    def __init__(self, name, view=None, manager=None):
        super(MenuView, self).__init__(name,
                                       icon=view.menu_icon,
                                       manager=manager)

        self._view = view

        view.menu = self

    def get_url(self):
        if self._view is None:
            return None

        url = self._view.href

        return url

