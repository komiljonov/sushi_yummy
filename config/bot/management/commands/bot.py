import os
from typing import Any
from django.core.management.base import BaseCommand

from tg_bot import Bot


# noinspection PyTypeChecker
class Command(BaseCommand):

    def handle(self, *args: Any, **options: Any):
        token = os.getenv("TOKEN")

        bot = Bot(token)

        bot.app.run_polling()
