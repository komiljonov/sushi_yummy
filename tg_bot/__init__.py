import base64
import os
from collections.abc import Callable, Coroutine

from django.db.models import QuerySet
from redis import Redis
from telegram import KeyboardButton
from telegram.ext import filters

from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    PreCheckoutQueryHandler,
)
from bot.models import User
from data.filial.models import Filial
from data.payment.models import Payment
from data.referral.models import Referral
from tg_bot.cart import TgBotCart
from tg_bot.feedback import TgBotFeedback
from tg_bot.menu import Menu
from tg_bot.redis_conversation import ConversationHandler
from tg_bot.constants import (
    CTX,
    EN,
    EXCLUDE,
    LANG,
    MAIN_MENU,
    REGISTER_NAME,
    REGISTER_PHONE,
    RU,
    UPD,
    UZ,
    INFO_FILIAL,
)
from utils import ReplyKeyboardMarkup, distribute, format_number_with_emojis
from utils.language import multilanguage
from data.cart.models import Cart
from django.utils import timezone


class Bot(Menu, TgBotCart, TgBotFeedback):

    def __init__(self, token: str):

        self.token = token

        self.redis = Redis.from_url("redis://redis:6379/0")

        self.CLICK_TOKEN = os.getenv("CLICK_TOKEN")
        self.PAYME_TOKEN = os.getenv("PAYME_TOKEN")

        self.ANYTHING = [
            CommandHandler("start", self.start),
        ]

        self.app = (
            ApplicationBuilder()
            .token(self.token)
            .concurrent_updates(128)
            .base_url("http://tgbotapi:8081/bot")
            .build()
        )

        self.app.add_handler(CommandHandler("load", self.reload_locale))
        self.app.add_handler(self._main_conversation())

        self.app.add_handler(PreCheckoutQueryHandler(self.pre_checkout_query_handler))

        self.app.add_handler(
            MessageHandler(filters.SUCCESSFUL_PAYMENT, self.successful_payment)
        )

    def _main_conversation(self):
        return ConversationHandler(
            "MainConversation",
            [
                CommandHandler("start", self.start),
                MessageHandler(filters.ALL & ~filters.SUCCESSFUL_PAYMENT, self.start),
            ],
            {
                LANG: [MessageHandler(filters.TEXT & EXCLUDE, self.lang)],
                REGISTER_NAME: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.register_name),
                    self.back(self.start),
                ],
                REGISTER_PHONE: [
                    MessageHandler(
                        filters.CONTACT | (filters.TEXT & EXCLUDE), self.register_number
                    ),
                    self.back(self.back_from_register_phone_number),
                ],
                MAIN_MENU: [
                    self._menu_handlers(),
                    self._feedback_handlers(),
                    self._cart_handlers(self.start),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("main_menu.contact")),
                        self.contact,
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("main_menu.info")), self.info
                    ),
                    MessageHandler(
                        filters.Text(multilanguage.get_all("main_menu.order_history")),
                        self.order_history,
                    ),
                    MessageHandler(
                        filters.Text(
                            multilanguage.get_all("main_menu.change_language")
                        ),
                        self.change_language,
                    ),
                ],
                INFO_FILIAL: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.info_filial),
                    self.back(self.start),
                ],
            },
            self.ANYTHING,
            redis=self.redis,
        )

    def back(self, callback: Callable[[UPD, CTX], Coroutine]) -> MessageHandler:
        return MessageHandler(
            filters.Text(multilanguage.get_all("buttons.back")), callback
        )

    async def main_menu_keyboard(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        keyboard = ReplyKeyboardMarkup(
            [
                [
                    i18n.main_menu.menu(),
                    i18n.menu.cart() if user.cart.items.count() > 0 else "",
                ],
                [i18n.main_menu.order_history(), i18n.main_menu.feedback()],
                [i18n.main_menu.info(), i18n.main_menu.contact()],
                [i18n.main_menu.change_language()],
            ],
            False,
        )
        return keyboard

    async def start(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        if context.args:
            if not user.referral:
                token = context.args[0]

                referral_id = base64.b64decode(token).decode()

                referral = Referral.objects.filter(id=referral_id).first()

                user.referral = referral
                user.save()

        if user.lang is None or user.name is None or user.number is None:
            await tg_user.send_message(
                i18n.register.lang.ask(),
                parse_mode="HTML",
                reply_markup=ReplyKeyboardMarkup([[UZ, RU], [EN]], False),
            )
            return LANG

        keyboard = await self.main_menu_keyboard(update, context)

        await tg_user.send_message("Menu", reply_markup=keyboard, parse_mode="HTML")

        return MAIN_MENU

    async def lang(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        lang = {UZ: "uz", RU: "ru", EN: "en"}.get(update.message.text)

        if lang is None:
            await tg_user.send_message(i18n.register.lang.wrong(), parse_mode="HTML")

            return await self.start(update, context)

        user.lang = lang
        user.save()

        if user.name is None or user.number is None:
            await tg_user.send_message(
                i18n.register.name.ask(),
                reply_markup=ReplyKeyboardMarkup(),
                parse_mode="HTML",
            )
            return REGISTER_NAME
        else:
            return await self.start(update, context)

    async def register_name(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        user.name = update.message.text
        user.save()

        await tg_user.send_message(
            i18n.register.number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
            parse_mode="HTML",
        )
        return REGISTER_PHONE

    async def register_number(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        phone = (
            update.message.contact.phone_number
            if update.message.contact
            else update.message.text
        )

        user.number = phone
        user.save()

        return await self.start(update, context)

    async def back_from_register_phone_number(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.register.name.ask(),
            reply_markup=ReplyKeyboardMarkup(),
            parse_mode="HTML",
        )

        return REGISTER_NAME

    async def reload_locale(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)
        multilanguage.load_translations("locales")

    async def pre_checkout_query_handler(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        _, _cartId, provider = update.pre_checkout_query.invoice_payload.split(":")

        cartId = base64.b64decode(_cartId.encode()).decode()

        cart = Cart.objects.filter(id=cartId).first()
        print(cart, update.pre_checkout_query)
        if cart is None:
            await update.pre_checkout_query.answer(
                False, "Kechirasiz buyurtma topilmadi."
            )

            return

        if cart.status not in ["ORDERING", "PENDING_PAYMENT"]:
            await update.pre_checkout_query.answer(
                False, "Kechirasiz buyurtma berib bo'lingan."
            )

            return

        await update.pre_checkout_query.answer(True)

    async def successful_payment(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        payment = update.message.successful_payment

        _, _cartId, provider = payment.invoice_payload.split(":")

        cart_id = base64.b64decode(_cartId.encode()).decode()

        cart = Cart.objects.filter(id=cart_id).first()

        if cart is None:
            return

        amount = payment.total_amount

        new_payment = Payment.objects.create(
            user=user, provider=provider, amount=amount, data=update.to_dict()
        )

        cart.status = "PENDING"
        cart.payment = new_payment
        cart.order_time = timezone.now()
        cart.save()

        await context.bot.send_message(
            cart.user.chat_id, i18n.payment.successful(), parse_mode="HTML"
        )

        return await self.start(update, context)

    async def contact(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(i18n.contact(), parse_mode="HTML")

    async def info(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)
        await tg_user.send_message(
            i18n.info.filial.ask(),
            reply_markup=ReplyKeyboardMarkup(
                distribute([i18n.get_name(filial) for filial in Filial.objects.all()]),
            ),
            parse_mode="HTML",
        )

        return INFO_FILIAL

    async def info_filial(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        filial = Filial.objects.filter(i18n.filter_name(update.message.text)).first()

        if filial is None:
            await tg_user.send_message(i18n.info.filial.not_found(), parse_mode="HTML")
            return INFO_FILIAL

        await tg_user.send_location(filial.location.latitude, filial.location.longitude)

        await tg_user.send_message(
            i18n.info.filial.info(
                name=i18n.get_name(filial),
            ),
            parse_mode="HTML",
        )

        return await self.start(update, context)

    async def order_history(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        carts: QuerySet[Cart] = user.carts.filter(
            status__in=["DONE", "CANCELLED", "PENDING_PAYMENT"]
        )

        print(carts)

        await tg_user.send_message("salom")

        for cart in carts:
            products_text = []

            for item in cart.items.all():
                products_text.append(
                    i18n.order_history.item(
                        count=format_number_with_emojis(item.count),
                        product_name=i18n.get_name(item.product),
                    )
                )

            await tg_user.send_message(
                i18n.order_history.info(
                    order_id=cart.order_id,
                    status=cart.status,
                    deliver_type=cart.delivery,
                    filial_or_address=(
                        i18n.order_history.location(address=cart.location.address)
                        if cart.location
                        else i18n.order_history.filial(
                            filial=i18n.get_name(cart.filial)
                        )
                    ),
                    products_text="\n".join(products_text),
                    payment=(
                        i18n.order_history.payment(payment_type=cart.payment.provider)
                        if cart.payment
                        else ""
                    ),
                    promocode=(
                        i18n.order_history.promocode(
                            name=cart.promocode.name,
                            amount=cart.promocode.amount,
                            measurement=cart.promocode.measurement,
                        )
                        if cart.promocode
                        else ""
                    ),
                    price=cart.discount_price,
                    delivery_price=0,
                    total_price=cart.price,
                )
            )

    async def change_language(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)
        print("Salom")
        await tg_user.send_message(
            i18n.register.lang.ask(),
            parse_mode="HTML",
            reply_markup=ReplyKeyboardMarkup([[UZ, RU], [EN]], False),
        )
        return LANG
