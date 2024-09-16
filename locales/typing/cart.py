from typing import Callable

dtype = Callable[[], str]



class Cart:
    instruction: dtype
    
