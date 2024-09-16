from typing import TYPE_CHECKING
from redis import Redis
from telegram import Update
from telegram.ext import filters

from telegram.ext import CommandHandler, MessageHandler
from bot.models import User

from tg_bot.redis_conversation import ConversationHandler
from utils.language import multilanguage

from tg_bot.constants import (
    CTX,
    EXCLUDE,
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


class Menu:

    redis: Redis

    def _menu_handlers(self):
        return ConversationHandler(
            "MenuConversation",
            [
                MessageHandler(
                    filters.Text(multilanguage.get_all("main_menu.menu")), self.menu
                )
            ],
            {
                MENU_CATEGORY: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.menu_category)
                ],
                MENU_PRODUCT: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.menu_product)
                ],
                PRODUCT_INFO: [
                    MessageHandler(filters.Regex(r"\d+"), self.set_product_count)
                ],
            },
            [CommandHandler("start", self.start)],
            self.redis,
            True,
            {MENU: MENU},
        )

    async def menu(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        temp.category = None
        temp.save()

        await tgUser.send_message(
            i18n.menu.welcome(),
            reply_markup=ReplyKeyboardMarkup(
                distribute(
                    [
                        i18n.get_name(category)
                        for category in Category.objects.filter(parent=None)
                    ]
                )
            ),
        )
        return MENU_CATEGORY

    async def menu_category(
        self, update: UPD, context: CTX, _category: "Category | None" = None
    ):
        tgUser, user, temp, i18n = User.get(update)

        category = (
            _category
            or Category.objects.filter(i18n.filter_name(update.message.text)).first()
        )

        if category == None:
            await tgUser.send_message(i18n.menu.category.not_found(), parse_mode="HTML")
            return await self.menu_category(update, context, temp.category)

        temp.category = category
        temp.save()

        await tgUser.send_message(
            i18n.menu.category.info(name=i18n.get_name(category)),
            reply_markup=ReplyKeyboardMarkup(
                distribute(
                    [i18n.get_name(product) for product in category.products.all()]
                )
            ),
        )
        return MENU_PRODUCT

    async def menu_product(self, update: UPD, context: CTX, _product: "Product" = None):
        tgUser, user, temp, i18n = User.get(update)

        product = temp.category.products.filter(
            i18n.filter_name(update.message.text)
        ).first()

        temp.product = product
        temp.save()

        image = product.image
        caption = i18n.get_value(product, "caption")

        if image == None:
            await tgUser.send_message(caption, parse_mode="HTML")
            return PRODUCT_INFO

        f = image.file.open("rb")

        await tgUser.send_photo(
            f,
            caption,
            reply_markup=ReplyKeyboardMarkup(distribute([i for i in "123456789"], 3)),
            parse_mode="HTML",
        )

        return PRODUCT_INFO

    async def set_product_count(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        product = temp.product

        count = int(update.message.text)

        cart.items.update_or_create(
            product=product, defaults=dict(price=product.price, count=count)
        )

        return await self.menu_category(update, context, product.category)
