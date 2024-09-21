#from collections.abc import Coroutine
from typing import Coroutine
from redis import Redis
from telegram.ext import MessageHandler
from typing import Callable

from data.category.models import Category
from tg_bot.constants import UPD, CTX


class CommonKeysMixin:
    redis: Redis

    ANYTHING: list

    start: Callable[[UPD, CTX], Coroutine[str | None]]
    back: Callable[[Callable[[UPD, CTX], Coroutine[str | None]]], MessageHandler]

    menu: Callable[[UPD, CTX], Coroutine[str | None]]
    menu_category: Callable[[UPD, CTX, Category], Coroutine[str | None]]