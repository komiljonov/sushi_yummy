import os
from typing import Generator, Optional
from rest_framework.views import APIView
from rest_framework.request import Request, HttpRequest
from django.http import StreamingHttpResponse

from bot.models import Location
from data.category.models import Category
from data.filial.models import Filial
from data.payment.models import PaymentType
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

        self.iiko_manager = Iiko(token)

        # Return a StreamingHttpResponse to stream the process
        return StreamingHttpResponse(
            self._sync_everything(),
            content_type="text/plain",
        )

    def _sync_everything(self) -> Generator[str, None, None]:
        organizations: list[Organization] = self.iiko_manager.get_organizations()

        yield "Starting synchronization...\n"

        for idx, organization in enumerate(organizations, start=1):

            self._sync_organization(organization)

            yield f"Synced organization {idx}/{len(organizations)}: {organization.name}\n"

        yield "Synchronization complete.\n"

    def _sync_organization(self, organization: Organization) -> None:

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

        filial.terminal_id = self.iiko_manager.get_terminal_id(organization)
        filial.save()

        # nomenclatures = self.iiko_manager.get_nomenclatures(organization.id)

        self._sync_products(filial)
        self._sync_payment_types(filial)

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

    def _sync_products(self, filial: Filial) -> None:

        nomenclatures = self.iiko_manager.get_nomenclatures(filial.iiko_id)

        # list[NomenclatureProduct]

        for product in nomenclatures.products:
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

    def _sync_payment_types(self, filial: Filial):

        payment_types = self.iiko_manager.get_payment_types(filial.iiko_id)

        for payment_type in payment_types:

            pt, created = PaymentType.objects.get_or_create(
                iiko_id=payment_type.id,
                defaults=dict(name=payment_type.name, code=payment_type.code),
            )

            pt.filials.add(filial)
            pt.save()
