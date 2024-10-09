from dataclasses import dataclass, field
from typing import Literal, Optional, List, Dict, Any


@dataclass
class Coordinates:
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class City:
    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class Street:
    id: Optional[str] = None
    name: Optional[str] = None
    city: Optional[City] = None


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


@dataclass
class DeliveryPoint:
    coordinates: Optional[Coordinates] = None
    address: Optional[Address] = None
    externalCartographyId: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class Customer:
    type: Optional[str] = None


@dataclass
class Order:
    parentDeliveryId: Optional[str] = None
    customer: Optional[Customer] = None
    phone: Optional[str] = None
    deliveryPoint: Optional[DeliveryPoint] = None
    status: Optional[str] = None
    status: Optional[
        Literal[
            "Unconfirmed",
            "WaitCooking",
            "ReadyForCooking",
            "CookingStarted",
            "CookingCompleted",
            "Waiting",
            "OnWay",
            "Delivered",
            "Closed",
            "Cancelled",
        ]
    ] = None
    # Add other fields as needed and ensure they are optional


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
    # Add other fields as needed


@dataclass
class DeliveryOrderUpdate:
    eventType: Optional[str] = None
    eventTime: Optional[str] = None
    organizationId: Optional[str] = None
    correlationId: Optional[str] = None
    eventInfo: Optional[EventInfo] = None
