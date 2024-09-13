from itertools import islice
from typing import Sequence
from telegram import ReplyKeyboardMarkup as RKM
from telegram._keyboardbutton import KeyboardButton
from typing import TypeVar


T = TypeVar("T")


from language import multilanguage, TranslationAccessor


class ReplyKeyboardMarkup(RKM):
    def __init__(
        self,
        _keyboard: Sequence[Sequence[str | KeyboardButton]] = None,
        back: bool = True,
        lang: TranslationAccessor | None = multilanguage.uz,
        resize_keyboard: bool | None = True,
        one_time_keyboard: bool | None = None,
        selective: bool | None = None,
        input_field_placeholder: str | None = None,
        is_persistent: bool | None = None,
    ):

        keyboard = _keyboard if _keyboard is not None else []

        if back:
            keyboard.append([lang.buttons.back()])

        super().__init__(
            keyboard,
            resize_keyboard,
            one_time_keyboard,
            selective,
            input_field_placeholder,
            is_persistent,
        )


def distribute(data: list[T], chunk_size: int = 2) -> list[T]:
    it = iter(data)
    return [
        list(islice(it, chunk_size))
        for _ in range((len(data) + chunk_size - 1) // chunk_size)
    ]
