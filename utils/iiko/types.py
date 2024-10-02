from dataclasses import dataclass, field
from typing import Any, Optional, List, Dict


@dataclass
class Organization:
    responseType: str
    id: str
    name: str
    code: str


@dataclass
class NomenclatureGroup:
    parentGroup: str
    id: str
    name: str
    children: List['NomenclatureGroup'] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[Dict]) -> List['NomenclatureGroup']:
        group_map = {item['id']: cls(
            id=item['id'],
            name=item['name'],
            parentGroup=item.get('parentGroup'),  # Use .get() for safety
        ) for item in data}

        # Create a mapping for children
        for group in group_map.values():
            if group.parentGroup:
                parent_group = group_map.get(group.parentGroup)
                if parent_group:
                    parent_group.children.append(group)

        # Return only top-level groups (those without a parent)
        return [group for group in group_map.values() if group.parentGroup is None]


@dataclass
class NomenclatureProduct:
    fatAmount: int
    proteinsAmount: int
    carbohydratesAmount: int
    energyAmount: int
    fatFullAmount: int
    proteinsFullAmount: int
    carbohydratesFullAmount: int
    energyFullAmount: int
    weight: float
    groupId: str
    productCategoryId: str
    type: str
    orderItemType: str
    modifierSchemaId: str
    modifierSchemaName: str
    splittable: bool
    measureUnit: str

    imageLinks: list
    doNotPrintInCheque: bool
    parentGroup: str
    order: int
    fullNameEnglish: str
    useBalanceForSell: bool
    canSetOpenPrice: bool
    paymentSubject: str
    id: str
    code: str
    name: str
    description: str
    additionalInfo: str
    tags: []
    isDeleted: bool
    seoDescription: str
    seoText: str
    seoKeywords: str
    seoTitle: str

    sizePrices: list
    modifiers: dict
    groupModifiers: list


@dataclass
class NomenclaturesResponse:
    correlationId: str

    groups: list[NomenclatureGroup]

    products: NomenclatureProduct =None
    productCategories: Optional[dict] = None
