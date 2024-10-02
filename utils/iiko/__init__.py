import requests
from .exceptions import InvalidTokenException
from .types import Organization, NomenclaturesResponse, NomenclatureGroup


class Iiko:
    BASE_URL = "https://api-ru.iiko.services/api/1/"

    def __init__(self, secret_token: str):
        self.secret_token = secret_token

        self.authenticated = False
        self.token = None

    def auth(self):
        req = requests.post(f"{self.BASE_URL}access_token", json={
            "apiLogin": self.secret_token
        })

        if req.status_code == 401:
            print(req.content)
            raise InvalidTokenException

        data = req.json()

        self.token = data['token']

        return True

    def get_organizations(self):
        req = requests.get(f"{self.BASE_URL}organizations", headers={
            "Authorization": f"Bearer {self.token}"
        })

        data = req.json()

        orgs = []

        for org in data['organizations']:
            orgs.append(
                Organization(
                    id=org['id'],
                    name=org['name'],
                    responseType=org['responseType'],
                    code=org['code']
                )
            )
        return orgs

    def get_nomenclatures(self, organization_id: str):
        print(organization_id)
        req = requests.post(f"{self.BASE_URL}nomenclature", json={
            "organizationId": organization_id
        }, headers={
            "Authorization": f"Bearer {self.token}"
        })

        data = req.json()

        res = NomenclaturesResponse(
            correlationId=data['correlationId'],
            groups=NomenclatureGroup.from_list(data['groups'])
        )




        return res