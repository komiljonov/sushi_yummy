from typing import Callable

from locales.typing.cart import Cart
from locales.typing.main_menu import MainMenu
from locales.typing.menu import Menu
from locales.typing.register import Register

dtype = Callable[[], str]


class Buttons:
    back: dtype
    create: dtype
    delete: dtype
    delete_all: dtype
    yes: dtype
    no: dtype
    cancel: dtype
    next: dtype
    phone_number: dtype


class MultiLanguageTranslations:
    buttons: Buttons
    welcome: dtype

    main_menu: MainMenu
    menu: Menu
    cart: Cart
    register: Register

    uz: dtype
    ru: dtype
