from typing import TYPE_CHECKING, Callable
from redis import Redis
from telegram.ext import filters

from telegram.ext import CommandHandler, MessageHandler
from bot.models import User

from tg_bot.menu.back import MenuBack
from tg_bot.redis_conversation import ConversationHandler
from utils.language import multilanguage

from tg_bot.constants import (
    CART,
    CTX,
    MAIN_MENU,
    MENU,
    MENU_CATEGORY,
    MENU_PRODUCT,
    PRODUCT_INFO,
    UPD,
)
from utils import ReplyKeyboardMarkup


class Cart:

    redis: Redis

    def _cart_handlers(self, back_handler: Callable[[UPD, CTX], str] | None = None):
        self.back_handler = back_handler
        return ConversationHandler(
            "CartConversation",
            [
                MessageHandler(
                    filters.Text(multilanguage.get_all("menu.cart")), self.cart
                )
            ],
            {CART: [self.back(self.back_handler or self.start)]},
            [
                CommandHandler("start", self.start),
                MessageHandler(filters.ALL, self.start),
            ],
            self.redis,
            True,
            {
                MENU: MENU,
                MAIN_MENU: MAIN_MENU,
                MENU_CATEGORY: MENU_CATEGORY,
                MENU_PRODUCT: MENU_PRODUCT,
                PRODUCT_INFO: PRODUCT_INFO,
            },
        )
        
        
        

    async def cart(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message(
            i18n.cart.instruction(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.buttons.back(), i18n.buttons.clear()]], False
            ),
            parse_mode="HTML",
        )

        items = user.cart.items.all()

        items_text = []
        total_price = 0

        for i, item in enumerate(items, 1):
            product_name = (
                i18n.get_name(item.product) if item.product else "Unnamed product"
            )

            item_price = item.price * item.count
            total_price += item_price
            # items_text += f"{i}. {product_name}\n\t\t\t\t{item.count} x {item.price:,.0f} = {item_price:,.0f} so'm\n\n"
            items_text.append(
                i18n.cart.item(
                    i=i,
                    product_name=product_name,
                    count=item.count,
                    price=item.price,
                    item_price=item_price,
                )
            )

        text = i18n.cart.info(products="".join(items_text), total_price=total_price)

        await tgUser.send_message(text)

        return CART
