import requests
from .exceptions import InvalidTokenException
from .types import (
    NomenclatureProduct,
    Organization,
    NomenclaturesResponse,
    NomenclatureGroup,
)


class Iiko:
    BASE_URL = "https://api-ru.iiko.services/api/1/"

    def __init__(self, secret_token: str):
        self.secret_token = secret_token

        self.authenticated = False
        self.token = None

    def auth(self):
        req = requests.post(
            f"{self.BASE_URL}access_token", json={"apiLogin": self.secret_token}
        )

        if req.status_code == 401:
            print(req.content)
            raise InvalidTokenException

        data = req.json()

        self.token = data["token"]

        return True

    def get_organizations(self):
        req = requests.get(
            f"{self.BASE_URL}organizations",
            headers={"Authorization": f"Bearer {self.token}"},
        )

        data = req.json()

        orgs = []

        for org in data["organizations"]:
            orgs.append(
                Organization(
                    id=org["id"],
                    name=org["name"],
                    responseType=org["responseType"],
                    code=org["code"],
                )
            )
        return orgs

    def get_nomenclatures(self, organization_id: str):
        print(organization_id)
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
                else None
            )

            # Print when a product with price is found
            if price is not None:
                print(f"Product with price found: {product['name']}, Price: {price}")

            if (
                product.get("modifiers") is None or len(product["modifiers"]) == 0
            ) and product["type"] == "Dish":
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
