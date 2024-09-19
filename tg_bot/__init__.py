import base64
import os
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
from data.payment.models import Payment
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
)
from utils import ReplyKeyboardMarkup
from utils.language import multilanguage
from data.cart.models import Cart


class Bot(Menu, TgBotCart, TgBotFeedback):

    def __init__(self, token: str):

        self.token = token

        self.redis = Redis.from_url("redis://redis:6379/0")

        self.CLICK_TOKEN = os.getenv("CLICK_TOKEN")
        self.PAYME_TOKEN = os.getenv("PAYME_TOKEN")

        self.ANYTHING = [
            CommandHandler("start", self.start),
            MessageHandler(filters.ALL & ~filters.SUCCESSFUL_PAYMENT, self.start),
        ]

        self.app = (
            ApplicationBuilder()
            .token(self.token)
            .concurrent_updates(128)
            .base_url("http://tgbotapi:8081/bot")
            # .bot()
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
                ],
            },
            self.ANYTHING,
            redis=self.redis,
        )

    def back(self, callback):
        return MessageHandler(
            filters.Text(multilanguage.get_all("buttons.back")), callback
        )

    async def main_menu_keyboard(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        keyboard = ReplyKeyboardMarkup(
            [
                [
                    i18n.main_menu.menu(),
                    i18n.menu.cart() if user.cart.items.count() > 0 else "",
                ],
                [i18n.main_menu.order_history(), i18n.main_menu.feedback()],
                [i18n.main_menu.info(), i18n.main_menu.contact()],
                [i18n.main_menu.settings()],
            ],
            False,
        )
        return keyboard

    async def start(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        if user.lang == None or user.name == None or user.number == None:
            await tgUser.send_message(
                i18n.register.lang.ask(),
                parse_mode="HTML",
                reply_markup=ReplyKeyboardMarkup([[UZ, RU], [EN]], False),
            )
            return LANG

        keyboard = await self.main_menu_keyboard(update, context)

        await tgUser.send_message("Menu", reply_markup=keyboard, parse_mode="HTML")

        return MAIN_MENU

    async def lang(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        lang = {UZ: "uz", RU: "ru", EN: "en"}.get(update.message.text)

        if lang == None:
            await tgUser.send_message(i18n.register.lang.wrong(), parse_mode="HTML")

            return await self.start(update, context)

        user.lang = lang
        user.save()

        await tgUser.send_message(
            i18n.register.name.ask(),
            reply_markup=ReplyKeyboardMarkup(),
        )

        return REGISTER_NAME

    async def register_name(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        user.name = update.message.text
        user.save()

        await tgUser.send_message(
            i18n.register.number.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [[KeyboardButton(i18n.buttons.phone_number(), request_contact=True)]]
            ),
        )
        return REGISTER_PHONE

    async def register_number(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        phone = (
            update.message.contact.phone_number
            if update.message.contact
            else update.message.text
        )

        user.number = phone
        user.save()

        return await self.start(update, context)

    async def back_from_register_phone_number(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        await tgUser.send_message(
            i18n.register.name.ask(),
            reply_markup=ReplyKeyboardMarkup(),
        )

        return REGISTER_NAME

    async def reload_locale(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)
        multilanguage.load_translations("locales")

    async def pre_checkout_query_handler(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        _, _cartId, provider = update.pre_checkout_query.invoice_payload.split(":")

        cartId = base64.b64decode(_cartId.encode()).decode()

        cart = Cart.objects.filter(id=cartId).first()
        print(cart, update.pre_checkout_query)
        if cart == None:
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
        tgUser, user, temp, i18n = User.get(update)

        payment = update.message.successful_payment

        _, _cartId, provider = payment.invoice_payload.split(":")

        cartId = base64.b64decode(_cartId.encode()).decode()

        cart = Cart.objects.filter(id=cartId).first()

        if cart == None:

            return

        amount = payment.total_amount

        new_payment = Payment.objects.create(
            user=user, provider=provider, amount=amount, data=update.to_dict()
        )

        cart.status = "PENDING"
        cart.payment = new_payment
        cart.save()

        await context.bot.send_message(
            cart.user.chat_id,
            i18n.payment.successful(),
        )

        return await self.start(update, context)
