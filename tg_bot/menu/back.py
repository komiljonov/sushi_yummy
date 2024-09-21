from bot.models import User

from tg_bot.constants import (
    CTX,
    UPD,
)

from tg_bot.common_file import CommonKeysMixin

class MenuBack(CommonKeysMixin):
    async def back_from_product_info(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        return await self.menu_category(update, context, temp.category)

    async def back_from_menu_category(self, update: UPD, context: CTX):
        tg_user, user, temp, i18n = User.get(update)

        return await self.menu(update, context)
