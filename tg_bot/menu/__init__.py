from typing import TYPE_CHECKING
from redis import Redis
from telegram.ext import filters

from telegram.ext import CommandHandler, MessageHandler
from bot.models import User

from tg_bot.menu.back import MenuBack
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


class Menu(MenuBack):

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
                    self._cart_handlers(self.menu),
                    MessageHandler(filters.TEXT & EXCLUDE, self.menu_category),
                    self.back(self.start),
                ],
                MENU_PRODUCT: [
                    self._cart_handlers(self.back_to_menu_product),
                    MessageHandler(filters.TEXT & EXCLUDE, self.menu_product),
                    self.back(self.back_from_menu_category),
                ],
                PRODUCT_INFO: [
                    self._cart_handlers(self.back_to_menu_product_info),
                    MessageHandler(filters.Regex(r"\d+"), self.set_product_count),
                    self.back(self.back_from_product_info),
                ],
            },
            self.ANYTHING,
            self.redis,
            True,
            {MENU: MENU, MAIN_MENU: MAIN_MENU},
        )

    async def menu(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        temp.category = None
        temp.product = None
        temp.save()

        await tgUser.send_message(
            i18n.menu.welcome(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
                    *distribute(
                        [
                            i18n.get_name(category)
                            for category in Category.objects.filter(parent=None)
                        ],
                    ),
                ]
            ),
            parse_mode="HTML",
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
            if temp.category == None:
                return await self.menu(update, context)
            return await self.menu_category(update, context, temp.category)

        temp.category = category
        temp.save()

        await tgUser.send_message(
            i18n.menu.category.info(name=i18n.get_name(category)),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
                    *distribute(
                        [i18n.get_name(product) for product in category.products.all()],
                    ),
                ]
            ),
            parse_mode="HTML",
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

        await tgUser.send_message(i18n.menu.product.count.ask(), parse_mode="HTML")

        return PRODUCT_INFO

    async def set_product_count(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        product = temp.product

        count = int(update.message.text)

        cart.items.update_or_create(
            product=product, defaults=dict(price=product.price, count=count)
        )

        await tgUser.send_message(
            i18n.menu.product.count.success(product_name=i18n.get_name(product)),
            parse_mode="HTML",
        )

        return await self.menu_category(update, context, product.category)

    async def back_to_menu_product(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        if temp.category == None:
            return await self.menu(update, context)

        return await self.menu_category(update, context, temp.category)

    async def back_to_menu_product_info(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        return await self.menu_product(update, context, temp.product)
