from typing import TYPE_CHECKING
from redis import Redis
from telegram.ext import filters

from telegram.ext import CommandHandler, MessageHandler
from bot.models import User

from tg_bot.redis_conversation import ConversationHandler
from utils.language import multilanguage

from tg_bot.constants import (
    CTX,
    EXCLUDE,
    MAIN_MENU,
    MENU,
    MENU_CATEGORY,
    MENU_PRODUCT,
    PRODUCT_INFO,
    UPD,
)
from utils import ReplyKeyboardMarkup, distribute

from data.category.models import Category

if TYPE_CHECKING:
    from data.product.models import Product


class MenuBack:
    async def back_from_product_info(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        return await self.menu_category(update, context, temp.category)

    async def back_from_menu_category(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)
        
        
        return await self.menu(update,context)
    
    
    