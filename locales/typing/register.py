from typing import Callable

dtype = Callable[[], str]



class RegisterField:
    ask: dtype
    wrong: dtype


class Register:
    name: RegisterField
    number: RegisterField
    lang: RegisterField