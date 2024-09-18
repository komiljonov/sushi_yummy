from redis import Redis
from telegram import KeyboardButton
from telegram.ext import filters

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from bot.models import User
from tg_bot.cart import Cart
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


class Bot(Menu, Cart):

    def __init__(self, token: str):

        self.token = token

        self.redis = Redis.from_url("redis://redis:6379/0")

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

    def _main_conversation(self):
        return ConversationHandler(
            "MainConversation",
            [
                CommandHandler("start", self.start),
                MessageHandler(filters.ALL, self.start),
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
                MAIN_MENU: [self._menu_handlers(), self._cart_handlers(self.start)],
            },
            [
                CommandHandler("start", self.start),
                MessageHandler(filters.ALL, self.start),
            ],
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
                [i18n.main_menu.order_history(), i18n.main_menu.leave_appeal()],
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
