from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any


@dataclass
class Coordinates:
    latitude: Optional[float] = None
    longitude: Optional[float] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)


@dataclass
class City:
    id: Optional[str] = None
    name: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)


@dataclass
class Street:
    id: Optional[str] = None
    name: Optional[str] = None
    city: Optional[City] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        city_data = data.get("city")
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            city=City.from_dict(city_data) if city_data else None,
        )


@dataclass
class Region:

    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Address:
    street: Optional[Street] = None
    index: Optional[str] = None
    house: Optional[str] = None
    building: Optional[str] = None
    flat: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[str] = None
    doorphone: Optional[str] = None
    region: Optional[Region] = None
    line1: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        street_data = data.get("street")
        return cls(
            street=Street.from_dict(street_data) if street_data else None,
            index=data.get("index"),
            house=data.get("house"),
            building=data.get("building"),
            flat=data.get("flat"),
            entrance=data.get("entrance"),
            floor=data.get("floor"),
            doorphone=data.get("doorphone"),
            region=data.get("region", {}),
            line1=data.get("line1"),
        )


@dataclass
class DeliveryPoint:
    coordinates: Optional[Coordinates] = None
    address: Optional[Address] = None
    externalCartographyId: Optional[str] = None
    comment: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        coordinates_data = data.get("coordinates")
        address_data = data.get("address")
        return cls(
            coordinates=(
                Coordinates.from_dict(coordinates_data) if coordinates_data else None
            ),
            address=Address.from_dict(address_data) if address_data else None,
            externalCartographyId=data.get("externalCartographyId"),
            comment=data.get("comment"),
        )


@dataclass
class Customer:
    id: Optional[str] = None
    name: Optional[str] = None
    surname: Optional[str] = None
    comment: Optional[str] = None
    gender: Optional[str] = None
    inBlacklist: Optional[bool] = False
    blacklistReason: Optional[str] = None
    birthdate: Optional[str] = None

    type: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        return cls(**data)


@dataclass
class CancelCause:
    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class CancelInfo:
    whenCancelled: Optional[str] = None
    cause: Optional[CancelCause] = None
    comment: Optional[str] = None


@dataclass
class CourierInfoCourier:
    id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None


@dataclass
class CourierInfo:
    courier: Optional[CourierInfoCourier] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    isCourierSelectedManually: Optional[bool] = False


@dataclass
class Problem:
    hasProblem: Optional[bool] = False
    description: Optional[str] = None


@dataclass
class Operator:
    id: Optional[str] = None
    name: Optional[str] = None
    phone: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, dict | str | None]):
        return cls(
            id=data.get('id'),
            name=data.get('name'),
            phone=data.get('phone'),
        )


@dataclass
class MarketingSource:
    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Order:
    parentDeliveryId: Optional[str] = None
    customer: Optional[Customer] = None
    phone: Optional[str] = None
    deliveryPoint: Optional[DeliveryPoint] = None
    status: Optional[str] = None
    cancelInfo: Optional[CancelInfo] = None
    completeBefore: Optional[str] = None
    comment: Optional[str] = None
    
    sum: float
    number: int

    operator: Optional[Operator] = None

    @classmethod
    def from_dict(cls, data: Dict[str, dict | str | None]):
        customer_data = data.get("customer")
        delivery_point_data = data.get("deliveryPoint")
        return cls(
            parentDeliveryId=data.get("parentDeliveryId"),
            customer=Customer.from_dict(customer_data) if customer_data else None,
            phone=data.get("phone"),
            deliveryPoint=(
                DeliveryPoint.from_dict(delivery_point_data)
                if delivery_point_data
                else None
            ),
            status=data.get("status"),
            comment=data.get("comment"),
            completeBefore=data.get("completeBefore"),
            sum=data.get('sum'),
            number=data.get('number'),
            operator=(
                Operator.from_dict(
                    operator_data
                )
                if (operator_data := data.get("operator"))
                else None
            ),
        )


@dataclass
class EventInfo:
    id: Optional[str] = None
    posId: Optional[str] = None
    externalNumber: Optional[str] = None
    organizationId: Optional[str] = None
    timestamp: Optional[int] = None
    creationStatus: Optional[str] = None
    errorInfo: Optional[Dict[str, Any]] = field(default_factory=dict)
    order: Optional[Order] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        order_data = data.get("order")
        return cls(
            id=data.get("id"),
            posId=data.get("posId"),
            externalNumber=data.get("externalNumber"),
            organizationId=data.get("organizationId"),
            timestamp=data.get("timestamp"),
            creationStatus=data.get("creationStatus"),
            errorInfo=data.get("errorInfo", {}),
            order=Order.from_dict(order_data) if order_data else None,
        )


@dataclass
class DeliveryOrderUpdate:
    eventType: Optional[str] = None
    eventTime: Optional[str] = None
    organizationId: Optional[str] = None
    correlationId: Optional[str] = None
    eventInfo: Optional[EventInfo] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        event_info_data = data.get("eventInfo")
        return cls(
            eventType=data.get("eventType"),
            eventTime=data.get("eventTime"),
            organizationId=data.get("organizationId"),
            correlationId=data.get("correlationId"),
            eventInfo=EventInfo.from_dict(event_info_data) if event_info_data else None,
        )


DeliveryOrderUpdate(
    eventType="DeliveryOrderUpdate",
    eventTime="2024-10-09 07:19:46.350",
    organizationId="e0e4f953-50b9-487d-8479-ec0220a85f9c",
    correlationId="c84fd645-c448-47c4-9cfd-01c5ddad173a",
    eventInfo=EventInfo(
        id="719685ca-b346-4e2e-a230-f058bb349704",
        posId="8a29705c-aa55-44db-88c6-8a39c50a1b7a",
        externalNumber="111516",
        organizationId="e0e4f953-50b9-487d-8479-ec0220a85f9c",
        timestamp=1728458386329,
        creationStatus="Success",
        errorInfo=None,
        order=Order(
            parentDeliveryId=None,
            customer=Customer(
                id="01ff6700-c042-fd4c-0191-e1c0c6979e5b",
                name="Муминов Тохиржон Бурханович",
                surname=None,
                comment=None,
                gender="NotSpecified",
                inBlacklist=False,
                blacklistReason=None,
                birthdate="1991-09-01 00:00:00.000",
                type="regular",
            ),
            phone="+998997777676",
            deliveryPoint=DeliveryPoint(
                coordinates=Coordinates(latitude=41.306021, longitude=69.278087),
                address=Address(
                    street=Street(
                        id="95f5a00d-f20f-4f38-9782-c8892d2e2f85",
                        name="Доставка",
                        city=City(
                            id="b090de0b-8550-6e17-70b2-bbba152bcbd3", name="Ташкент"
                        ),
                    ),
                    index="",
                    house="1",
                    building="",
                    flat="",
                    entrance="",
                    floor="",
                    doorphone="",
                    region=None,
                    line1=None,
                ),
                externalCartographyId=None,
                comment="АО Узавтосаноат, 13, Амира Темура проспект, Шараф Рашидов, Мирабадский район",
            ),
            status="CookingStarted",
        ),
    ),
)
