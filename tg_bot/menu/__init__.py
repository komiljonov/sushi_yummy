from typing import TYPE_CHECKING

from geopy.geocoders import Nominatim
from redis import Redis
from telegram import KeyboardButton
from telegram.ext import filters

from telegram.ext import MessageHandler
from bot.models import User
from data.filial.models import Filial

from tg_bot.menu.back import MenuBack
from tg_bot.redis_conversation import ConversationHandler
from utils.language import multilanguage

from tg_bot.constants import (
    CTX,
    EXCLUDE,
    LANG,
    MAIN_MENU,
    MENU,
    MENU_CATEGORY,
    MENU_PRODUCT,
    PRODUCT_INFO,
    REGISTER_NAME,
    REGISTER_PHONE,
    UPD,
    DELIVERY_LOCATION,
    CART_DELIVER_LOCATION_CONFIRM,
    CART_TAKEAWAY_FILIAL,
    MENU_GET_METHOD,
)
from utils import ReplyKeyboardMarkup, distribute, get_later_times

from data.category.models import Category

if TYPE_CHECKING:
    from data.product.models import Product

from tg_bot.common_file import CommonKeysMixin


class Menu(MenuBack, CommonKeysMixin):
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
                MENU_GET_METHOD: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.deliver")),
                        self.cart_get_method_deliver,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.take_away")),
                        self.cart_get_method_take_away,
                    ),
                    self.back(self.menu),
                ],
                DELIVERY_LOCATION: [
                    MessageHandler(filters.LOCATION, self.cart_delivery_location),
                    self.back(self.back_from_cart_delivery_location),
                ],
                CART_DELIVER_LOCATION_CONFIRM: [
                    MessageHandler(filters.LOCATION, self.cart_delivery_location),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.confirm")),
                        self.cart_deliver_location_confirm,
                    ),
                    self.back(self.back_from_cart_delivery_location_confirm),
                ],
                CART_TAKEAWAY_FILIAL: [
                    MessageHandler(
                        filters.LOCATION, self.cart_takeaway_filial_location
                    ),
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_takeaway_filial),
                    self.back(self.back_from_cart_takeaway_filial),
                ],
                MENU_CATEGORY: [
                    self._cart_handlers(self.menu),
                    MessageHandler(filters.TEXT & EXCLUDE, self.menu_category),
                    self.back(self.back_from_menu_category),
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
            {
                MENU: MENU,
                MAIN_MENU: MAIN_MENU,
                LANG: LANG,
                REGISTER_NAME: REGISTER_NAME,
                REGISTER_PHONE: REGISTER_PHONE,
            },
        )

    async def menu(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        temp.category = None
        temp.product = None
        temp.save()

        await tg_user.send_message(
            i18n.cart.get_method(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.cart.deliver(), i18n.cart.take_away()]]
            ),
            parse_mode="HTML",
        )
        print("Menu")

        return MENU_GET_METHOD

        # await tg_user.send_message(
        #     i18n.menu.welcome(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
        #             *distribute(
        #                 [
        #                     i18n.get_name(category)
        #                     for category in Category.objects.filter(parent=None)
        #                 ],
        #             ),
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return MENU_CATEGORY

    async def cart_get_method_deliver(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "DELIVER"
        cart.save()

        await tg_user.send_message(
            i18n.deliver.location.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [KeyboardButton(i18n.buttons.location(), request_location=True)],
                    [i18n.buttons.my_locations()],
                ]
            ),
            parse_mode="HTML",
        )
        return DELIVERY_LOCATION

    async def cart_delivery_location(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        location = update.message.location

        nominatim = Nominatim(user_agent="Google")

        address = nominatim.reverse(f"{location.latitude},{location.longitude}")

        new_location = user.locations.create(
            name=str(address),
            latitude=location.latitude,
            longitude=location.longitude,
            address=str(address),
        )

        temp.location = new_location
        temp.save()

        await tg_user.send_message(
            i18n.deliver.location.confirm(address=address),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(
                            i18n.deliver.location.resend(), request_location=True
                        )
                    ],
                    [i18n.buttons.confirm()],
                ]
            ),
            parse_mode="HTML",
        )

        return CART_DELIVER_LOCATION_CONFIRM

    async def cart_deliver_location_confirm(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.location = temp.location
        cart.save()

        # await tg_user.send_message(
        #     i18n.time.deliver(),
        #     reply_markup=ReplyKeyboardMarkup(
        #         [
        #             [
        #                 i18n.time.asap(),
        #             ],
        #             [i18n.time.later()],
        #         ]
        #     ),
        #     parse_mode="HTML",
        # )
        # return CART_TIME

        await tg_user.send_message(
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

    async def cart_get_method_take_away(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "TAKEAWAY"
        cart.save()

        filials = Filial.objects.filter(active=True)

        await tg_user.send_message(
            i18n.takeaway.filial.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        KeyboardButton(
                            i18n.takeaway.filial.check_nearest_filial(),
                            request_location=True,
                        )
                    ],
                    *distribute([i18n.get_name(filial) for filial in filials]),
                ]
            ),
            parse_mode="HTML",
        )

        return CART_TAKEAWAY_FILIAL

    async def cart_takeaway_filial_location(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        location = update.message.location

        filial: Filial | None = Filial.get_nearest_filial(location)

        filials = Filial.objects.filter(active=True)

        await tg_user.send_message(
            i18n.takeaway.filial.filial_info(filial=i18n.get_name(filial)),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [i18n.takeaway.filial.check_nearest_filial()],
                    *distribute([i18n.get_name(filial) for filial in filials]),
                ]
            ),
            parse_mode="HTML",
        )

    async def cart_takeaway_filial(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        filial = Filial.objects.filter(i18n.filter_name(update.message.text)).first()

        if filial is None:
            await tg_user.send_message(
                i18n.takeaway.filial.not_found(), parse_mode="HTML"
            )
            return await self.cart_get_method_take_away(update, context)

        cart = user.cart

        cart.filial = filial
        cart.save()

        await tg_user.send_message(
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
        tg_user, user, temp, i18n = User.get(update)

        category = (
            _category
            or Category.objects.filter(
                i18n.filter_name(update.message.text), parent=temp.category
            ).first()
        )

        if category is None:
            await tg_user.send_message(
                i18n.menu.category.not_found(), parse_mode="HTML"
            )
            if temp.category is None:
                return await self.menu(update, context)
            return await self.menu_category(update, context, temp.category)

        temp.category = category
        temp.save()

        user.category_visits.create(category=category)

        if category.content_type == "CATEGORY":
            await tg_user.send_message(
                i18n.menu.category.info(),
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
                        *distribute(
                            [i18n.get_name(cat) for cat in category.children.all()],
                        ),
                    ]
                ),
            )
            return MENU_CATEGORY
        else:

            await tg_user.send_message(
                i18n.menu.category.info(name=i18n.get_name(category)),
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [i18n.menu.cart() if user.cart.items.count() > 0 else ""],
                        *distribute(
                            [
                                i18n.get_name(product)
                                for product in category.products.all()
                            ],
                        ),
                    ]
                ),
                parse_mode="HTML",
            )
            return MENU_PRODUCT

    async def menu_product(self, update: UPD, context: CTX, _product: "Product" = None):
        tg_user, user, temp, i18n = User.get(update)

        product = temp.category.products.filter(
            i18n.filter_name(update.message.text)
        ).first()

        temp.product = product
        temp.save()

        user.product_visits.create(product=product)

        image = product.image
        _caption = i18n.get_value(product, "caption")

        caption = _caption if _caption else "Caption yo'q"

        if image is None:
            await tg_user.send_message(
                caption,
                reply_markup=ReplyKeyboardMarkup(
                    distribute([i for i in "123456789"], 3)
                ),
                parse_mode="HTML",
            )
            return PRODUCT_INFO

        f = image.file.open("rb")

        await tg_user.send_photo(
            f,
            caption if caption else "Caption yo'q",
            reply_markup=ReplyKeyboardMarkup(distribute([i for i in "123456789"], 3)),
            parse_mode="HTML",
        )

        await tg_user.send_message(i18n.menu.product.count.ask(), parse_mode="HTML")

        return PRODUCT_INFO

    async def set_product_count(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        product = temp.product

        count = int(update.message.text)

        cart.items.update_or_create(
            product=product, defaults=dict(price=product.price, count=count)
        )

        await tg_user.send_message(
            i18n.menu.product.count.success(product_name=i18n.get_name(product)),
            parse_mode="HTML",
        )

        return await self.menu_category(update, context, product.category)

    async def back_to_menu_product(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        if temp.category is None:
            return await self.menu(update, context)

        return await self.menu_category(update, context, temp.category)

    async def back_to_menu_product_info(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        return await self.menu_product(update, context, temp.product)

    async def back_from_menu_category(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        category = temp.category

        if category == None:

            if user.cart.delivery == "DELIVER":
                await tgUser.send_message(
                    i18n.deliver.location.ask(),
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [
                                KeyboardButton(
                                    i18n.buttons.location(), request_location=True
                                )
                            ],
                            [i18n.buttons.my_locations()],
                        ]
                    ),
                    parse_mode="HTML",
                )
                return DELIVERY_LOCATION
            else:
                await tgUser.send_message(
                    i18n.deliver.location.confirm(address=user.cart.location.address),
                    reply_markup=ReplyKeyboardMarkup(
                        [
                            [
                                KeyboardButton(
                                    i18n.deliver.location.resend(),
                                    request_location=True,
                                )
                            ],
                            [i18n.buttons.confirm()],
                        ]
                    ),
                    parse_mode="HTML",
                )

                return CART_DELIVER_LOCATION_CONFIRM
        else:
            # return await self.menu_category(update,context, category.parent)
            temp.category = None
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
