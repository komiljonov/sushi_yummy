import os
from telegram.ext import ContextTypes
from typing import TypeVar
from telegram import Update
from telegram.ext.filters import Text

CTX = TypeVar("CTX", bound=ContextTypes.DEFAULT_TYPE)
UPD = TypeVar("UPD", bound=Update)


PASSWORD = os.getenv("PASSWORD")


EXCLUDE = ~Text(["/start", f"/start {PASSWORD}", f"/start basicUser"])


UZ = "🇺🇿 O'zbekcha"
RU = "🇷🇺 Русский"
EN = "🇺🇸 English"


MENU = "MENU"


MAIN_MENU = "MAIN_MENU"
LANG = "LANG"


MENU_CATEGORY = "MENU_CATEGORY"
MENU_PRODUCT = "MENU_PRODUCT"
PRODUCT_INFO ="PRODUCT_INFO"