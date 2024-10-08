import os
from typing import Generator, Optional
from rest_framework.views import APIView
from rest_framework.request import Request, HttpRequest
from django.http import StreamingHttpResponse

from bot.models import Location
from data.category.models import Category
from data.filial.models import Filial
from data.product.models import Product
from utils.iiko import Iiko, Organization, NomenclatureGroup
from utils.iiko.types import NomenclatureProduct


class SyncAPIView(APIView):

    def get(self, request: HttpRequest | Request) -> StreamingHttpResponse:
        token = os.getenv("IIKO_TOKEN", "")
        if not token:
            return StreamingHttpResponse(
                "No token available", status=400, content_type="text/plain"
            )

        iiko_manager = Iiko(token)
        # iiko_manager.auth()

        organizations = iiko_manager.get_organizations()

        # Return a StreamingHttpResponse to stream the process
        return StreamingHttpResponse(
            self._generate_state(iiko_manager, organizations), content_type="text/plain"
        )

    def _generate_state(
        self, iiko_manager: Iiko, organizations: list[Organization]
    ) -> Generator[str, None, None]:
        yield "Starting synchronization...\n"
        for idx, organization in enumerate(organizations, start=1):
            self._sync_organization(iiko_manager, organization)
            yield f"Synced organization {idx}/{len(organizations)}: {organization.name}\n"
        yield "Synchronization complete.\n"

    def _sync_organization(self, manager: Iiko, organization: Organization) -> None:

        filial, created = Filial.objects.get_or_create(
            iiko_id=organization.id,
        )

        if created:
            filial.name_uz = organization.name
            filial.name_ru = organization.name
            filial.location = Location.objects.create(
                name=organization.name,
                latitude=organization.latitude,
                longitude=organization.longitude,
                address=organization.name,
                used=True,
                special=True,
            )
            filial.save()

        filial.terminal_id = manager.get_terminal_id(organization)
        filial.save()

        nomenclatures = manager.get_nomenclatures(organization.id)


        self._sync_products(nomenclatures.products, filial)

    def _sync_categories(self, groups: list[NomenclatureGroup], filial: Filial) -> None:
        for group in groups:
            Category.objects.get_or_create(
                defaults=dict(
                    name_uz=group.name,
                    name_ru=group.name,
                    filial=filial,
                ),
            )

    def _link_categories(self, groups: list[NomenclatureGroup]) -> None:
        for group in groups:
            category = Category.objects.filter(iiko_id=group.id).first()
            if category:
                category.parent = Category.objects.filter(
                    iiko_id=group.parentGroup
                ).first()
                category.save()

    def _sync_products(
        self, products: list[NomenclatureProduct], filial: Filial
    ) -> None:
        for product in products:
            if product.price == 0:
                continue

            new_product, created = Product.objects.get_or_create(
                iiko_id=product.id,
                defaults=dict(price=product.price),
            )

            if created:
                new_product.name_uz = product.name
                new_product.name_ru = product.name
                new_product.save()

            new_product.filials.add(filial)
