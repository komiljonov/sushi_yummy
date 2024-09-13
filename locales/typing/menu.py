from typing import Callable

dtype = Callable[[], str]


class Category:
    not_found: dtype
    info: dtype
    welcome: dtype


class Menu:
    category: Category
