from redis import Redis
from telegram.ext import filters

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler
from bot.models import User
from redis_conversation import ConversationHandler
from tg_bot.constants import CTX, EN, EXCLUDE, LANG, MAIN_MENU, MENU, RU, UPD, UZ
from utils import ReplyKeyboardMarkup


class Bot:

    def __init__(self, token: str):

        self.token = token

        self.redis = Redis.from_url("redis://redis:6379/0")

        self.app = (
            ApplicationBuilder()
            .token(self.token)
            .concurrent_updates(128)
            .base_url("http://tgbotapi:8081/bot")
            .build()
        )

    def _main_conversation(self):
        return ConversationHandler(
            "MainConversation",
            [CommandHandler("start", self.start)],
            {
                MAIN_MENU: [self._menu_handlers()],
                LANG: [MessageHandler(filters.TEXT & EXCLUDE, self.lang)],
            },
            [CommandHandler("start", self.start)],
            redis=self.redis,
        )

    async def main_menu_keyboard(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        keyboard = ReplyKeyboardMarkup(
            [
                [
                    i18n.main_menu.menu(),
                ],
                [i18n.main_menu.order_history(), i18n.main_menu.leave_appeal()],
                [i18n.main_menu.info(), i18n.main_menu.contact()],
                [i18n.main_menu.settings()],
            ]
        )

    async def start(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        if user.lang == None:
            await tgUser.send_message(
                i18n.lang.ask(),
                parse_mode="HTML",
                reply_markup=ReplyKeyboardMarkup([[UZ, RU], [EN]], True),
            )
            return LANG

        keyboard = self.main_menu_keyboard()

        return MAIN_MENU

    async def lang(self, update: UPD, context: CTX):
        tgUser, user, temp, i18n = User.get(update)

        lang = {UZ: "uz", RU: "ru", EN: "en"}.get(update.message.text)

        if lang == None:
            await tgUser.send_message(i18n.lang.wrong())

            return await self.lang(update, context)

        user.lang = lang
        user.save()

        return await self.start(update, context)
