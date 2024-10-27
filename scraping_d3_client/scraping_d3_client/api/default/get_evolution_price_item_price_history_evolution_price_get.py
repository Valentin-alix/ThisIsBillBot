from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.http_validation_error import HTTPValidationError
from ...models.quantity_enum import QuantityEnum
from ...models.read_item_price_history_schema import ReadItemPriceHistorySchema
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    server_id: int,
    type_id: int,
    item_gid: Union[None, Unset, int] = UNSET,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    params["server_id"] = server_id

    params["type_id"] = type_id

    json_item_gid: Union[None, Unset, int]
    if isinstance(item_gid, Unset):
        json_item_gid = UNSET
    else:
        json_item_gid = item_gid
    params["item_gid"] = json_item_gid

    json_quantity: Union[Unset, int] = UNSET
    if not isinstance(quantity, Unset):
        json_quantity = quantity.value

    params["quantity"] = json_quantity

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/item_price_history/evolution_price",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ReadItemPriceHistorySchema.from_dict(response_200_item_data)

            response_200.append(response_200_item)

        return response_200
    if response.status_code == 422:
        response_422 = HTTPValidationError.from_dict(response.json())

        return response_422
    if client.raise_on_unexpected_status:
        raise errors.UnexpectedStatus(response.status_code, response.content)
    else:
        return None


def _build_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Response[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    server_id: int,
    type_id: int,
    item_gid: Union[None, Unset, int] = UNSET,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Response[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    """Get Evolution Price

    Args:
        server_id (int):
        type_id (int):
        item_gid (Union[None, Unset, int]):
        quantity (Union[Unset, QuantityEnum]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ReadItemPriceHistorySchema']]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        type_id=type_id,
        item_gid=item_gid,
        quantity=quantity,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    server_id: int,
    type_id: int,
    item_gid: Union[None, Unset, int] = UNSET,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    """Get Evolution Price

    Args:
        server_id (int):
        type_id (int):
        item_gid (Union[None, Unset, int]):
        quantity (Union[Unset, QuantityEnum]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ReadItemPriceHistorySchema']]
    """

    return sync_detailed(
        client=client,
        server_id=server_id,
        type_id=type_id,
        item_gid=item_gid,
        quantity=quantity,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    server_id: int,
    type_id: int,
    item_gid: Union[None, Unset, int] = UNSET,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Response[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    """Get Evolution Price

    Args:
        server_id (int):
        type_id (int):
        item_gid (Union[None, Unset, int]):
        quantity (Union[Unset, QuantityEnum]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ReadItemPriceHistorySchema']]]
    """

    kwargs = _get_kwargs(
        server_id=server_id,
        type_id=type_id,
        item_gid=item_gid,
        quantity=quantity,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    server_id: int,
    type_id: int,
    item_gid: Union[None, Unset, int] = UNSET,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Optional[Union[HTTPValidationError, list["ReadItemPriceHistorySchema"]]]:
    """Get Evolution Price

    Args:
        server_id (int):
        type_id (int):
        item_gid (Union[None, Unset, int]):
        quantity (Union[Unset, QuantityEnum]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ReadItemPriceHistorySchema']]
    """

    return (
        await asyncio_detailed(
            client=client,
            server_id=server_id,
            type_id=type_id,
            item_gid=item_gid,
            quantity=quantity,
        )
    ).parsed
