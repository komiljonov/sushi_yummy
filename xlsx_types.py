from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Location:
    id: str
    name: Optional[str]
    latitude: float
    longitude: float
    address: str


@dataclass
class Filial:
    id: str
    name_uz: str
    name_ru: str
    location: Optional[Location]


@dataclass
class Product:
    id: str
    todays_sells: int
    sale_count: int
    image: Optional[str]
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    name_uz: str
    name_ru: str
    iiko_id: str
    caption_uz: str
    caption_ru: str
    price: float
    category: Optional[str]
    filials: List[str]


@dataclass
class Item:
    id: str
    product: Product
    count: int
    price: float
    total_price: float


@dataclass
class Promocode:
    id: str
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    name: str
    code: str
    measurement: str
    amount: int
    count: int
    end_date: str
    is_limited: bool
    is_max_limited: bool
    min_amount: float
    max_amount: float


@dataclass
class User:
    id: str
    has_order: bool
    created_at: str
    updated_at: str
    deleted_at: Optional[str]
    chat_id: int
    name: str
    number: str
    tg_name: str
    username: str
    lang: str
    last_update: Optional[str]
    referral: str


@dataclass
class Order:
    id: str
    order_id: Optional[str]
    user: User
    phone_number: str
    products_count: int
    promocode: Optional[Promocode]
    order_time: str
    time: str
    status: str
    price: float
    discount_price: float
    saving: float
    items: List[Item]
    comment: Optional[str]
    payment: Optional[str]
    filial: Optional[Filial]
    location: Optional[Location]
    taxi: Optional[str]


@dataclass
class OrderList:
    orders: List[Order] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[dict]):
        def parse_location(location_data):
            if location_data:
                return Location(
                    id=location_data["id"],
                    name=location_data.get("name"),
                    latitude=location_data["latitude"],
                    longitude=location_data["longitude"],
                    address=location_data["address"],
                )
            return None

        def parse_filial(filial_data):
            if filial_data:
                return Filial(
                    id=filial_data["id"],
                    name_uz=filial_data["name_uz"],
                    name_ru=filial_data["name_ru"],
                    location=parse_location(filial_data.get("location")),
                )
            return None

        def parse_product(product_data):
            return Product(
                id=product_data["id"],
                todays_sells=product_data["todays_sells"],
                sale_count=product_data["sale_count"],
                image=product_data.get("image"),
                created_at=product_data["created_at"],
                updated_at=product_data["updated_at"],
                deleted_at=product_data.get("deleted_at"),
                name_uz=product_data["name_uz"],
                name_ru=product_data["name_ru"],
                iiko_id=product_data["iiko_id"],
                caption_uz=product_data["caption_uz"],
                caption_ru=product_data["caption_ru"],
                price=product_data["price"],
                category=product_data.get("category"),
                filials=product_data["filials"],
            )

        def parse_items(items_data):
            return [
                Item(
                    id=item["id"],
                    product=parse_product(item["product"]),
                    count=item["count"],
                    price=item["price"],
                    total_price=item["total_price"],
                )
                for item in items_data
            ]

        def parse_promocode(promocode_data):
            if promocode_data:
                return Promocode(
                    id=promocode_data["id"],
                    created_at=promocode_data["created_at"],
                    updated_at=promocode_data["updated_at"],
                    deleted_at=promocode_data.get("deleted_at"),
                    name=promocode_data["name"],
                    code=promocode_data["code"],
                    measurement=promocode_data["measurement"],
                    amount=promocode_data["amount"],
                    count=promocode_data["count"],
                    end_date=promocode_data["end_date"],
                    is_limited=promocode_data["is_limited"],
                    is_max_limited=promocode_data["is_max_limited"],
                    min_amount=promocode_data["min_amount"],
                    max_amount=promocode_data["max_amount"],
                )
            return None

        def parse_user(user_data):
            return User(
                id=user_data["id"],
                has_order=user_data["has_order"],
                created_at=user_data["created_at"],
                updated_at=user_data["updated_at"],
                deleted_at=user_data.get("deleted_at"),
                chat_id=user_data["chat_id"],
                name=user_data["name"],
                number=user_data["number"],
                tg_name=user_data["tg_name"],
                username=user_data["username"],
                lang=user_data["lang"],
                last_update=user_data.get("last_update"),
                referral=user_data["referral"],
            )

        orders = [
            Order(
                id=order_data["id"],
                order_id=order_data.get("order_id"),
                user=parse_user(order_data["user"]),
                phone_number=order_data["phone_number"],
                products_count=order_data["products_count"],
                promocode=parse_promocode(order_data.get("promocode")),
                order_time=order_data["order_time"],
                time=order_data["time"],
                status=order_data["status"],
                price=order_data["price"],
                discount_price=order_data["discount_price"],
                saving=order_data["saving"],
                items=parse_items(order_data["items"]),
                comment=order_data.get("comment"),
                payment=order_data.get("payment"),
                filial=parse_filial(order_data.get("filial")),
                location=parse_location(order_data.get("location")),
                taxi=order_data.get("taxi"),
            )
            for order_data in data
        ]
        return cls(orders=orders)
