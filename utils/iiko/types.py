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
    children: List["NomenclatureGroup"] = field(default_factory=list)

    @classmethod
    def from_list(cls, data: List[Dict]) -> List["NomenclatureGroup"]:
        group_map = {
            item["id"]: cls(
                id=item["id"],
                name=item["name"],
                parentGroup=item.get("parentGroup"),  # Use .get() for safety
            )
            for item in data
        }

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
    id: str
    code: str
    name: str
    parentGroup: str
    type: str
    productCategoryId: str
    price: float
    
    # sizePrices: list
    isDeleted: bool
    
    
    


@dataclass
class NomenclaturesResponse:
    correlationId: str

    groups: list[NomenclatureGroup]

    products: list[NomenclatureProduct] = None
    productCategories: Optional[dict] = None
