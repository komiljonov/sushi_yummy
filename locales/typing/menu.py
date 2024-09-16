from typing import Callable

dtype = Callable[[], str]


class Category:
    not_found: dtype
    info: dtype
    welcome: dtype
    
    
    
class ProductCount:
    ask: dtype
    success: dtype
    
class Product:
    count: ProductCount

class Menu:
    category: Category
    product: Product
