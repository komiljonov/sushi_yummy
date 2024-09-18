import os
from telegram.ext import ContextTypes
from typing import TypeVar
from telegram import Update
from telegram.ext.filters import Text
from utils.language import multilanguage

CTX = TypeVar("CTX", bound=ContextTypes.DEFAULT_TYPE)
UPD = TypeVar("UPD", bound=Update)


PASSWORD = os.getenv("PASSWORD")


EXCLUDE = ~Text(
    [
        "/start",
        f"/start {PASSWORD}",
        f"/start basicUser",
        *multilanguage.get_all("buttons.back"),
    ]
)


UZ = "🇺🇿 O'zbekcha"
RU = "🇷🇺 Русский"
EN = "🇺🇸 English"

CLICK = "CLICK"
PAYME = "PAYME"
CASH = "CASH"

MENU = "MENU"

REGISTER_NAME = "REGISTER_NAME"
REGISTER_PHONE = "REGISTER_PHONE"

MAIN_MENU = "MAIN_MENU"
LANG = "LANG"


MENU_CATEGORY = "MENU_CATEGORY"
MENU_PRODUCT = "MENU_PRODUCT"
PRODUCT_INFO = "PRODUCT_INFO"


CART = "CART"

CART_GET_METHOD = "CART_GET_METHOD"

DELIVERY_LOCATION = "DELIVERY_LOCATION"
CART_DELIVER_LOCATION_CONFIRM = "CART_DELIVER_LOCATION_CONFIRM"
CART_TAKEAWAY_FILIAL = "CART_TAKEAWAY_FILIAL"
CART_TIME = "CART_TIME"


CART_TIME_LATER_TIME = "CART_TIME_LATER_TIME"


CART_PHONE_NUMBER = "CART_PHONE_NUMBER"

CART_COMMENT = "CART_COMMENT"


CART_COUPON = "CART_COUPON"

CART_CONFIRM = "CART_CONFIRM"


PAYMENT_METHOD = "PAYMENT_METHOD"
