import datetime
from collections.abc import Mapping
from typing import Any, TypeVar, Union, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field
from dateutil.parser import isoparse

from ..models.quantity_enum import QuantityEnum

T = TypeVar("T", bound="ReadItemPriceHistorySchema")


@_attrs_define
class ReadItemPriceHistorySchema:
    """
    Attributes:
        name (str):
        quantity (QuantityEnum):
        price (Union[None, int]):
        recorded_at (datetime.datetime):
    """

    name: str
    quantity: QuantityEnum
    price: Union[None, int]
    recorded_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        quantity = self.quantity.value

        price: Union[None, int]
        price = self.price

        recorded_at = self.recorded_at.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "quantity": quantity,
                "price": price,
                "recorded_at": recorded_at,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        name = d.pop("name")

        quantity = QuantityEnum(d.pop("quantity"))

        def _parse_price(data: object) -> Union[None, int]:
            if data is None:
                return data
            return cast(Union[None, int], data)

        price = _parse_price(d.pop("price"))

        recorded_at = isoparse(d.pop("recorded_at"))

        read_item_price_history_schema = cls(
            name=name,
            quantity=quantity,
            price=price,
            recorded_at=recorded_at,
        )

        read_item_price_history_schema.additional_properties = d
        return read_item_price_history_schema

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
