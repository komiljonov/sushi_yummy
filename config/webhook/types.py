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
class Address:
    street: Optional[Street] = None
    index: Optional[str] = None
    house: Optional[str] = None
    building: Optional[str] = None
    flat: Optional[str] = None
    entrance: Optional[str] = None
    floor: Optional[str] = None
    doorphone: Optional[str] = None
    region: Optional[Dict[str, str]] = field(default_factory=dict)
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
class Order:
    parentDeliveryId: Optional[str] = None
    customer: Optional[Customer] = None
    phone: Optional[str] = None
    deliveryPoint: Optional[DeliveryPoint] = None
    status: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
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
