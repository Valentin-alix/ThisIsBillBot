from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.quantity_enum import QuantityEnum

T = TypeVar("T", bound="CreateItemPriceHistorySchema")


@_attrs_define
class CreateItemPriceHistorySchema:
    """
    Attributes:
        gid (int):
        quantity (QuantityEnum):
        price (Union[None, int]):
        server_id (int):
    """

    gid: int
    quantity: QuantityEnum
    price: Union[None, int]
    server_id: int
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        gid = self.gid

        quantity = self.quantity.value

        price: Union[None, int]
        price = self.price

        server_id = self.server_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "gid": gid,
                "quantity": quantity,
                "price": price,
                "server_id": server_id,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        gid = d.pop("gid")

        quantity = QuantityEnum(d.pop("quantity"))

        def _parse_price(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        price = _parse_price(d.pop("price"))

        server_id = d.pop("server_id")

        create_item_price_history_schema = cls(
            gid=gid,
            quantity=quantity,
            price=price,
            server_id=server_id,
        )

        create_item_price_history_schema.additional_properties = d
        return create_item_price_history_schema

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
