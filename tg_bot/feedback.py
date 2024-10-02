from telegram.ext import filters

from telegram.ext import (
    MessageHandler,
)
from bot.models import User
from data.feedback.models import Feedback, Service
from tg_bot.redis_conversation import ConversationHandler
from tg_bot.constants import (
    CTX,
    EXCLUDE,
    FEEDBACK_COMMENT,
    FEEDBACK_SERVICE,
    FEEDBACK_STAR,
    LANG,
    MAIN_MENU,
    UPD,
)
from utils import ReplyKeyboardMarkup, distribute
from utils.language import multilanguage
from tg_bot.common_file import CommonKeysMixin


class TgBotFeedback(CommonKeysMixin):

    def _feedback_handlers(self):
        return ConversationHandler(
            "FeedbackConversation",
            [
                MessageHandler(
                    filters.Text(multilanguage.get_all("main_menu.feedback")),
                    self.feedback,
                )
            ],
            {
                FEEDBACK_STAR: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.feedback_stars),
                    self.back(self.start),
                ],
                FEEDBACK_SERVICE: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.feedback_service),
                    self.back(self.feedback),
                ],
                FEEDBACK_COMMENT: [
                    MessageHandler(filters.TEXT & EXCLUDE, self.feedback_comment),
                    self.back(self.back_from_feedback_comment),
                ],
            },
            self.ANYTHING,
            self.redis,
            True,
            {
                MAIN_MENU: MAIN_MENU,
                LANG: LANG,
            },
        )

    async def feedback(self, update: UPD, context: CTX) -> str | None:
        tg_user, user, temp, i18n = User.get(update)

        await tg_user.send_message(
            i18n.feedback.star.ask(),
            reply_markup=ReplyKeyboardMarkup(
                [
                    [i18n.feedback.star.levels.best()],
                    [i18n.feedback.star.levels.good()],
                    [i18n.feedback.star.levels.not_like()],
                    [i18n.feedback.star.levels.bad()],
                    [i18n.feedback.star.levels.worst()],
                ]
            ),
            parse_mode="HTML",
        )
        return FEEDBACK_STAR

    async def feedback_stars(self, update: UPD, context: CTX) -> str | None:
        tg_user, user, temp, i18n = User.get(update)

        levels = {
            i18n.feedback.star.levels.best(): 5,
            i18n.feedback.star.levels.good(): 4,
            i18n.feedback.star.levels.not_like(): 3,
            i18n.feedback.star.levels.bad(): 2,
            i18n.feedback.star.levels.worst(): 1,
        }

        level = levels.get(update.message.text)

        if level is None:
            await tg_user.send_message(i18n.feedback.star.not_found(), parse_mode="HTML")
            return FEEDBACK_STAR

        temp.star = level
        temp.save()

        if level < 5:
            services = Service.objects.filter(active=True)
            await tg_user.send_message(
                i18n.feedback.bad_service.ask(),
                reply_markup=ReplyKeyboardMarkup(
                    distribute([i18n.get_name(service) for service in services])
                ),
                parse_mode="HTML",
            )
            return FEEDBACK_SERVICE

        await tg_user.send_message(
            i18n.feedback.comment(),
            reply_markup=ReplyKeyboardMarkup(),
            parse_mode="HTML",
        )
        return FEEDBACK_COMMENT

    async def feedback_service(self, update: UPD, context: CTX) -> str | None:
        tg_user, user, temp, i18n = User.get(update)

        service = Service.objects.filter(i18n.filter_name(update.message.text)).first()

        if service is None:
            await tg_user.send_message(
                i18n.feedback.bad_service.not_found(), parse_mode="HTML"
            )
            return FEEDBACK_SERVICE

        await tg_user.send_message(
            i18n.feedback.comment(),
            reply_markup=ReplyKeyboardMarkup(),
            parse_mode="HTML",
        )
        return FEEDBACK_COMMENT

    async def feedback_comment(self, update: UPD, context: CTX) -> str | None | int:
        tg_user, user, temp, i18n = User.get(update)

        new_feedback = Feedback.objects.create(
            user=user, service=temp.service, comment=update.message.text, star=temp.star
        )

        await tg_user.send_message(i18n.feedback.success(), parse_mode="HTML")

        return -1

    async def back_from_feedback_comment(self, update: UPD, context: CTX) -> str | None:
        tg_user, user, temp, i18n = User.get(update)

        if temp.star < 5:
            services = Service.objects.filter(active=True)
            await tg_user.send_message(
                i18n.feedback.bad_service.ask(),
                reply_markup=ReplyKeyboardMarkup(
                    distribute([i18n.get_name(service) for service in services])
                ),
                parse_mode="HTML",
            )
            return FEEDBACK_SERVICE

        return await self.feedback(update, context)
