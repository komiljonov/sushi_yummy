from telegram import KeyboardButton

from bot.models import User
from geopy.geocoders import Nominatim
from data.filial.models import Filial

from tg_bot.constants import (
    CART_COMMENT,
    CART_DELIVER_LOCATION_CONFIRM,
    CART_GET_METHOD,
    CART_PHONE_NUMBER,
    CART_TAKEAWAY_FILIAL,
    CART_TIME,
    CART_TIME_LATER_TIME,
    CTX,
    DELIVERY_LOCATION,
    UPD,
    CART_PROMOCODE,
)
from utils import ReplyKeyboardMarkup, distribute, get_later_times
from utils.geocoder import reverse_geocode


class CartBack:

    async def back_from_cart_delivery_location(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.cart.get_method(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.cart.deliver(), i18n.cart.take_away()]]
            ),
            parse_mode="HTML",
        )

        return CART_GET_METHOD

    async def back_from_cart_delivery_location_confirm(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

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

    async def back_from_cart_takeaway_filial(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.cart.get_method(),
            reply_markup=ReplyKeyboardMarkup(
                [[i18n.cart.deliver(), i18n.cart.take_away()]]
            ),
            parse_mode="HTML",
        )

        return CART_GET_METHOD

    async def back_from_cart_time(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        if cart.delivery == "DELIVER":

            address = reverse_geocode(cart.location.latitude, cart.location.longitude)

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
        else:
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

    async def back_from_cart_time_later_time(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        await tg_user.send_message(
            (
                i18n.time.deliver()
                if cart.delivery == "DELIVER"
                else i18n.time.takeaway()
            ),
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

    async def back_from_cart_phone_number(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        cart = user.cart

        if cart.time:
            times = get_later_times()
            text = (
                i18n.time.ask_later_deliver()
                if cart.delivery == "DELIVER"
                else i18n.time.ask_later_takeaway()
            )

            await tg_user.send_message(
                text,
                reply_markup=ReplyKeyboardMarkup(
                    distribute([time.strftime("%H:%M") for time in times])
                ),
                parse_mode="HTML",
            )
            return CART_TIME_LATER_TIME

        cart = user.cart

        await tg_user.send_message(
            (
                i18n.time.deliver()
                if cart.delivery == "DELIVER"
                else i18n.time.takeaway()
            ),
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

    async def back_from_cart_comment(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.data.phone_number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
        )
        return CART_PHONE_NUMBER

    async def back_from_cart_coupon(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.data.comment.ask(),
            reply_markup=ReplyKeyboardMarkup([[KeyboardButton(i18n.buttons.skip())]]),
            parse_mode="HTML",
        )
        return CART_COMMENT

    async def back_from_cart_confirm(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.order.promocode.ask(),
            reply_markup=ReplyKeyboardMarkup([[i18n.buttons.skip()]]),
            parse_mode="HTML",
        )

        return CART_PROMOCODE

    async def back_from_payment_method(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        return await self.cart_promocode(update, context, user.cart.promocode or 0)
