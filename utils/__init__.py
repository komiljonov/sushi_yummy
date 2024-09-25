from datetime import datetime, timedelta
from itertools import islice
from typing import Sequence
from telegram import ReplyKeyboardMarkup as RKM
from telegram._keyboardbutton import KeyboardButton
from typing import TypeVar


T = TypeVar("T")


from .language import multilanguage, TranslationAccessor


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


def get_later_times(start_time=None):
    if start_time is None:
        start_time = datetime.now() + timedelta(hours=1)
    else:
        start_time = start_time + timedelta(hours=1)

    # Set the start time to the next occurrence of the hour with minutes set to 30
    if start_time.minute >= 30:
        start_time = start_time.replace(minute=30, second=0, microsecond=0)

    else:
        start_time = start_time.replace(minute=30, second=0, microsecond=0)

    # Generate intervals for the next 3 hours
    intervals = [start_time + timedelta(minutes=i * 30) for i in range(0, 6)]
    return intervals


def format_number_with_emojis(number):
    # Dictionary for mapping digits to emojis
    numbers = {
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
        "0": "0️⃣"
    }

    # Convert the number to a string and replace each digit with the corresponding emoji
    formatted_number = ''.join([numbers[digit] for digit in str(number) if digit in numbers])
    return formatted_number