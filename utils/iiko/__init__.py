from time import sleep
from typing import TYPE_CHECKING
from datetime import datetime, timedelta
import requests

from .exceptions import InvalidTokenException
from .types import (
    NomenclatureProduct,
    Organization,
    NomenclaturesResponse,
    NomenclatureGroup,
    PaymentType,
)

if TYPE_CHECKING:
    from data.cart.models import Cart
    from data.filial.models import Filial


class Iiko:
    BASE_URL = "https://api-ru.iiko.services/api/1/"
    TOKEN_VALID_DURATION = timedelta(hours=1)  # Token is valid for 1 hour

    def __init__(self, secret_token: str):
        self.secret_token = secret_token
        self._token = None
        self._last_auth_time = None

    @property
    def token(self):
        # Check if token is expired or doesn't exist
        if self._token is None or self._is_token_expired():
            self._reauth()  # Refresh the token if expired or doesn't exist
        return self._token

    def _is_token_expired(self) -> bool:
        # If no last auth time, consider the token expired
        if self._last_auth_time is None:
            return True
        # Calculate time since last authentication
        time_since_auth = datetime.now() - self._last_auth_time
        # Token expires after 40 minutes, so refresh if more time has passed
        return time_since_auth > timedelta(minutes=40)

    def _reauth(self):
        # Re-authenticate by sending a POST request to obtain a new token
        req = requests.post(
            f"{self.BASE_URL}access_token", json={"apiLogin": self.secret_token}
        )
        if req.status_code == 401:
            print(req.content)
            raise InvalidTokenException

        data = req.json()
        self._token = data["token"]
        self._last_auth_time = datetime.now()  # Store the last authentication time

    def get_organizations(self):
        req = requests.get(
            f"{self.BASE_URL}organizations",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        data = req.json()

        orgs = [org["id"] for org in data["organizations"]]

        # for org in data["organizations"]:
        #     orgs.append(
        #         Organization(
        #             id=org["id"],
        #             name=org["name"],
        #             responseType=org["responseType"],
        #             code=org["code"],
        #         )
        #     )

        return self.get_organizations_data(orgs)

    def get_organizations_data(self, organizations: list[str]):

        req = requests.post(
            f"{self.BASE_URL}organizations/settings",
            headers={"Authorization": f"Bearer {self.token}"},
            json={
                "organizationIds": organizations,
                "includeDisabled": True,
                "parameters": ["name", "latitude", "longitude"],
            },
        )

        print(req.text)

        data = req.json()

        res = []

        for org in data["organizations"]:

            res.append(
                Organization(
                    id=org["id"],
                    name=org["name"],
                    latitude=org["latitude"],
                    longitude=org["longitude"],
                )
            )

        return res

    def get_nomenclatures(self, organization_id: str):

        req = requests.post(
            f"{self.BASE_URL}nomenclature",
            json={"organizationId": organization_id},
            headers={"Authorization": f"Bearer {self.token}"},
        )

        data = req.json()

        products = []
        for product in data["products"]:
            # if product['order'] == 0:
            # continue
            price = (
                product["sizePrices"][0]["price"]["currentPrice"]
                if product.get("sizePrices")
                and len(product["sizePrices"]) > 0
                and "price" in product["sizePrices"][0]
                and product["sizePrices"][0]["price"][
                    "isIncludedInMenu"
                ]  # New condition added
                else None
            )

            # Print when a product with price is found
            if price is not None:
                print(f"Product with price found: {product['name']}, Price: {price}")

            # if (
            #     product.get("modifiers") is None or len(product["modifiers"]) == 0
            # ) and product["type"] == "Dish":
            #     continue

            if price == None:
                continue

            # Append the product to the list
            products.append(
                NomenclatureProduct(
                    id=product["id"],
                    code=product["code"],
                    name=product["name"],
                    parentGroup=product["parentGroup"],
                    type=product["type"],
                    productCategoryId=product["productCategoryId"],
                    isDeleted=product["isDeleted"],
                    price=price,
                )
            )

        res = NomenclaturesResponse(
            correlationId=data["correlationId"],
            # groups=NomenclatureGroup.from_list(data["groups"]),
            groups=[
                NomenclatureGroup(
                    id=group["id"], name=group["name"], parentGroup=group["parentGroup"]
                )
                for group in data["groups"]
            ],
            products=products,
        )

        return res

    def get_request_state(self, filial: "Filial", correlationId: str):
        res = requests.post(
            f"{self.BASE_URL}commands/status",
            json={"organizationId": filial.iiko_id, "correlationId": correlationId},
            headers={"Authorization": f"Bearer {self.token}"},
        )

        print(res.text)

        if res.status_code != 200:
            return False

        return res.json().get("state") == "Success"

    def _creat_order(self, cart: "Cart"):
        payment_type = cart.get_payment_type()
        data = {
            "organizationId": cart.filial.iiko_id,
            "terminalGroupIds": cart.filial.terminal_id,
            "order": {
                "externalNumber": cart.order_id,
                "orderServiceType": (
                    "DeliveryByCourier"
                    if cart.delivery == "DELIVER"
                    else "DeliveryByClient"
                ),
                "customer": {
                    "name": cart.user.name,
                    "surname": cart.user.username or "NoUsername",
                    "comment": cart.comment,
                },
                "phone": cart.phone_number,
                "items": [
                    {
                        "productId": item.product.iiko_id,
                        "amount": item.count,
                        "type": "Product",
                    }
                    for item in cart.items.all()
                ],
                "externalData": [
                    {
                        "key": "TaxiIdKomiljonov",
                        "value": "Salom Ishladi external data",
                        "isPublic": True,
                    }
                ],
            },
        }

        if payment_type:
            data["order"]["payment"] = [
                (
                    {
                        "paymentTypeId": payment_type.iiko_id,
                        "sum": cart.payment.amount,
                        "isProcessedExternally": True,
                        "isPrepay": True,
                    }
                )
            ]

        # Conditionally add the Address key if the delivery is not "DELIVER"
        if cart.delivery == "DELIVER":
            data["order"]["deliveryPoint"] = {
                "coordinates": {
                    "latitude": cart.location.latitude,
                    "longitude": cart.location.longitude,
                },
                "externalCartographyId": str(cart.location.id),
            }

        res = requests.post(
            f"{self.BASE_URL}deliveries/create",
            json=data,
            headers={"Authorization": f"Bearer {self.token}"},
        )

        print("ORder State Main State", res.status_code)
        print("ORder State Main", res.text)

        if res.status_code == 200:
            return True, res.json()

        return False, res

    def create_order(self, cart: "Cart"):

        success, _order = self._creat_order(cart)

        cart.correlation_id = _order["correlationId"]
        cart.save()

        if not success:
            print(_order.text)

            cart.correlation_id = _order.json()["correlationId"]
            cart.save()
            return None

        sleep(2)

        state = self.get_request_state(cart.filial, _order["correlationId"])

        print("State", "state")

        if not state:
            return None

        cart.iiko_id = _order["orderInfo"]["id"]

        cart.save()

        return _order

    def get_terminal_id(self, organization: Organization):

        res = requests.post(
            f"{self.BASE_URL}terminal_groups",
            json={"organizationIds": [organization.id]},
            headers={"Authorization": f"Bearer {self.token}"},
        )

        print(res, res.text)
        return res.json()["terminalGroups"][0]["items"][0]["id"]

    def get_payment_types(self, organization_id: str):

        req = requests.post(
            f"{self.BASE_URL}payment_types",
            json={"organizationIds": [organization_id]},
            headers={"Authorization": f"Bearer {self.token}"},
        )

        data = req.json()

        payment_types: list[PaymentType] = []

        for payment_type in data["paymentTypes"]:

            payment_types.append(
                PaymentType(
                    id=payment_type["id"],
                    name=payment_type["name"],
                    code=payment_type["code"],
                    organization_id=payment_type["terminalGroups"][0]["organizationId"],
                )
            )

        return payment_types
