import asyncio
from datetime import date, datetime, timedelta
from typing import Callable
from redis import Redis
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, Message
from telegram.ext import filters, CallbackQueryHandler

from telegram.ext import CommandHandler, MessageHandler
from bot.models import Location, User
from geopy.geocoders import Nominatim, Yandex
from data.filial.models import Filial
from tg_bot.cart.back import CartBack
from tg_bot.redis_conversation import ConversationHandler
from utils.language import multilanguage

from tg_bot.constants import (
    CART,
    CART_COMMENT,
    CART_CONFIRM,
    CART_COUPON,
    CART_DELIVER_LOCATION_CONFIRM,
    CART_GET_METHOD,
    CART_PHONE_NUMBER,
    CART_TAKEAWAY_FILIAL,
    CART_TIME,
    CART_TIME_LATER_TIME,
    CTX,
    DELIVERY_LOCATION,
    EXCLUDE,
    LANG,
    MAIN_MENU,
    MENU,
    MENU_CATEGORY,
    MENU_PRODUCT,
    PRODUCT_INFO,
    UPD,
)
from utils import ReplyKeyboardMarkup, distribute, get_later_times


class Cart(CartBack):

    redis: Redis

    def _cart_handlers(self, back_handler: Callable[[UPD, CTX], str] | None = None):
        # self.back_handler = back_handler
        return ConversationHandler(
            "CartConversation",
            [
                MessageHandler(
                    filters.Text(multilanguage.get_all("menu.cart")), self.cart
                )
            ],
            {
                CART: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.done")), self.cart_done
                    ),
                    CallbackQueryHandler(self.cart_set_count, pattern=r"set_count"),
                    CallbackQueryHandler(self.cart_remove_item, pattern=r"remove"),
                    self.back(self.back_from_cart(back_handler)),
                ],
                CART_GET_METHOD: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.deliver")),
                        self.cart_get_method_deliver,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("cart.take_away")),
                        self.cart_get_method_take_away,
                    ),
                    self.back(self.cart),
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
                CART_TIME: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_time),
                    self.back(self.back_from_cart_time),
                ],
                CART_TIME_LATER_TIME: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_time_later_time),
                    self.back(self.back_from_cart_time_later_time),
                ],
                CART_PHONE_NUMBER: [
                    MessageHandler(
                        filters.CONTACT | (filters.TEXT & EXCLUDE),
                        self.cart_phone_number,
                    ),
                    self.back(self.back_from_cart_phone_number),
                ],
                CART_COMMENT: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_comment),
                    self.back(self.back_from_cart_comment),
                ],
                CART_COUPON: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.cart_coupon),
                    self.back(self.back_from_cart_coupon),
                ],
                CART_CONFIRM: [
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.confirm")),
                        self.cart_confirm,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("buttons.cancel")),
                        self.cart_reject,
                    ),
                ],
            },
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
                LANG: LANG,
            },
        )

    async def cart_keyboard(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        items = user.cart.items.all()

        keyboard = []

        for i, item in enumerate(items, 1):

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"{i}. {i18n.get_name(item.product)} ❌",
                        callback_data=f"remove:{item.id}",
                    )
                ]
            )

            row = []

            if item.count > 0:
                row.append(
                    InlineKeyboardButton(
                        "➖", callback_data=f"set_count:reduce:{item.id}"
                    )
                )

            row.append(
                InlineKeyboardButton(f"{item.count}", callback_data=f"info:{item.id}")
            )

            row.append(
                InlineKeyboardButton(
                    f"➕", callback_data=f"set_count:increase:{item.id}"
                )
            )
            keyboard.append(row)

        return InlineKeyboardMarkup(keyboard)

    async def cart(self, update: UPD, context: CTX, edit: bool = False):
        tgUser, user, temp, i18n = User.get(update)

        if not edit:
            instruction = await tgUser.send_message(
                i18n.cart.instruction(),
                reply_markup=ReplyKeyboardMarkup(
                    [[i18n.buttons.back(), i18n.buttons.clear()], [i18n.cart.done()]],
                    False,
                ),
                parse_mode="HTML",
            )

            temp.cmid2 = instruction.message_id
            temp.save()

        items = user.cart.items.all()

        if items.count() == 0:
            await tgUser.send_message(i18n.cart.empty(), parse_mode="HTML")
            await self.delete_messages(update, context)
            return await self.start(update, context)

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
        keyboard = await self.cart_keyboard(update, context)
        if not edit:

            new_message = await tgUser.send_message(
                text,
                parse_mode="HTML",
                reply_markup=keyboard,
            )
            temp.cmid = new_message.message_id
            temp.save()
        else:
            message: Message = update.callback_query.message

            await message.edit_text(text, parse_mode="HTML", reply_markup=keyboard)

        return CART

    async def cart_set_count(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        _, action, itemId = update.callback_query.data.split(":")

        item = user.cart.items.filter(id=itemId).first()

        if item == None:
            # TODO: Impelement error text
            await update.callback_query.answer()
            return

        item.count += 1 if action == "increase" else -1
        item.save()

        return await self.cart(update, context, True)

    async def cart_remove_item(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        action, itemId = update.callback_query.data.split(":")

        item = user.cart.items.filter(id=itemId).first()

        if item == None:
            # TODO: Impelement error text
            await update.callback_query.answer()
            return

        item.delete()

        return await self.cart(update, context, True)

    def back_from_cart(self, callback: Callable):
        async def wrap(update: UPD, context: CTX):
            tgUser, user, temp, i18n = User.get(update)

            # Prioritize callback first
            result = await callback(update, context)

            # Execute both delete_message calls concurrently
            await self.delete_messages(update, context)

            return result

        return wrap

    async def delete_messages(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        try:
            await asyncio.gather(
                tgUser.delete_message(temp.cmid), tgUser.delete_message(temp.cmid2)
            )
        except Exception as e:
            print(e)

    async def cart_done(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message(
            i18n.cart.get_method(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.cart.deliver(), i18n.cart.take_away()]]
            ),
            parse_mode="HTML",
        )
        await self.delete_messages(update, context)

        return CART_GET_METHOD

    async def cart_get_method_deliver(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "DELIVER"
        cart.save()

        await tgUser.send_message(
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
        tgUser, user, temp, i18n = User.get(update)

        location = update.message.location

        nominatim = Nominatim(user_agent="Google")

        address = nominatim.reverse(f"{location.latitude},{location.longitude}")

        new_location = user.locations.create(
            name=str(address),
            latitude=location.latitude,
            longitude=location.longitude,
        )

        temp.location = new_location
        temp.save()

        await tgUser.send_message(
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
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.location = temp.location
        cart.save()

        await tgUser.send_message(
            i18n.time.deliver(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        i18n.time.asap(),
                    ],
                    [i18n.time.later()],
                ]
            ),
            parse_mode="HTML",
        )
        return CART_TIME

    async def cart_get_method_take_away(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        cart.delivery = "TAKEAWAY"
        cart.save()

        filials = Filial.objects.filter(active=True)

        await tgUser.send_message(
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
        tgUser, user, temp, i18n = User.get(update)

        location = update.message.location

        filial: Filial | None = Filial.get_nearest_filial(location)

        filials = Filial.objects.filter(active=True)

        await tgUser.send_message(
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
        tgUser, user, temp, i18n = User.get(update)

        filial = Filial.objects.filter(i18n.filter_name(update.message.text)).first()

        if filial == None:
            await tgUser.send_message(
                i18n.takeaway.filial.not_found(), parse_mode="HTML"
            )
            return await self.cart_get_method_take_away(update, context)

        cart = user.cart

        cart.filial = filial
        cart.save()

        await tgUser.send_message(
            i18n.time.takeaway(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [
                        i18n.time.asap(),
                    ],
                    [i18n.time.later()],
                ]
            ),
            parse_mode="HTML",
        )
        return CART_TIME

    async def cart_time(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        if update.message.text == i18n.time.later():
            times = get_later_times()
            text = (
                i18n.time.ask_later_deliver()
                if cart.delivery == "DELIVER"
                else i18n.time.ask_later_takeaway()
            )

            await tgUser.send_message(
                text,
                reply_markup=ReplyKeyboardMarkup(
                    distribute([time.strftime("%H:%M") for time in times])
                ),
                parse_mode="HTML",
            )
            return CART_TIME_LATER_TIME

        if update.message.text == i18n.time.asap():
            await tgUser.send_message(
                i18n.data.phone_number.ask(),
                reply_markup=ReplyKeyboardMarkup(
                    [
                        [
                            KeyboardButton(
                                i18n.buttons.phone_number(), request_contact=True
                            )
                        ]
                    ]
                ),
            )
            return CART_PHONE_NUMBER

        await tgUser.send_message(i18n.time.wrong())
        return CART_TIME_LATER_TIME

    async def cart_time_later_time(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        time_t = update.message.text

        # Parse the time string into a datetime object, ensuring it's interpreted as today's date
        time = datetime.combine(date.today(), datetime.strptime(time_t, "%H:%M").time())

        time = time if time > datetime.now() else time + timedelta(days=1)

        print(time)

        # temp.time = time
        # temp.save()
        cart = user.cart
        cart.time = time
        cart.save()

        # TODO: Implement payment

        await tgUser.send_message(
            i18n.data.phone_number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
        )
        return CART_PHONE_NUMBER

    async def cart_time_asap(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message(
            i18n.data.phone_number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
        )
        return CART_PHONE_NUMBER

    async def cart_phone_number(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        phone = (
            update.message.contact.phone_number
            if update.message.contact
            else update.message.text
        )

        print(phone)

        cart = user.cart
        cart.phone_number = phone
        cart.save()

        await tgUser.send_message(
            i18n.order.comment.ask(),
            reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
        )
        return CART_COMMENT

    async def cart_comment(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart
        cart.comment = (
            update.message.text if update.message.text != i18n.buttons.skip() else None
        )

        cart.save()

        await tgUser.send_message(
            i18n.order.coupon.aks(),
            reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
        )

        return CART_COUPON

    async def cart_coupon(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        cart = user.cart

        products_text = []

        for i, item in enumerate(cart.items.all(), 1):

            products_text.append(
                (
                    f"{i}. {i18n.get_name(obj=item.product)}\n"
                    f"{item.count} x {item.price} = {item.count * item.price}"
                )
            )

        await tgUser.send_message(
            i18n.order.info(
                name=user.name,
                number=cart.phone_number,
                delivery_method=cart.delivery,
                comment=cart.comment,
                filial=i18n.get_name(cart.filial),
                total_price=cart.price,
                orders="\n".join(products_text),
            ),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.buttons.confirm(), i18n.buttons.cancel()]]
            ),
        )

        return CART_CONFIRM

    async def cart_confirm(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message("Qabul qilindi.")

    async def cart_reject(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message("Rad etildi qilindi.")
