from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.get_sales_speed_by_gid_item_price_history_get_sales_speed_post_response_get_sales_speed_by_gid_item_price_history_get_sales_speed_post import (
    GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
)
from ...models.http_validation_error import HTTPValidationError
from ...models.quantity_enum import QuantityEnum
from ...types import UNSET, Response, Unset


def _get_kwargs(
    *,
    body: list[int],
    server_id: int,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> dict[str, Any]:
    headers: dict[str, Any] = {}

    params: dict[str, Any] = {}

    params["server_id"] = server_id

    json_quantity: Union[Unset, int] = UNSET
    if not isinstance(quantity, Unset):
        json_quantity = quantity.value

    params["quantity"] = json_quantity

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "post",
        "url": "/item_price_history/get_sales_speed",
        "params": params,
    }

    _kwargs["json"] = body

    headers["Content-Type"] = "application/json"

    _kwargs["headers"] = headers
    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    if response.status_code == 200:
        response_200 = GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost.from_dict(
            response.json()
        )

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
) -> Response[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[int],
    server_id: int,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Response[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    """Get Sales Speed By Gid

    Args:
        server_id (int):
        quantity (Union[Unset, QuantityEnum]):
        body (list[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        server_id=server_id,
        quantity=quantity,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[int],
    server_id: int,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Optional[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    """Get Sales Speed By Gid

    Args:
        server_id (int):
        quantity (Union[Unset, QuantityEnum]):
        body (list[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost, HTTPValidationError]
    """

    return sync_detailed(
        client=client,
        body=body,
        server_id=server_id,
        quantity=quantity,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[int],
    server_id: int,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Response[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    """Get Sales Speed By Gid

    Args:
        server_id (int):
        quantity (Union[Unset, QuantityEnum]):
        body (list[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost, HTTPValidationError]]
    """

    kwargs = _get_kwargs(
        body=body,
        server_id=server_id,
        quantity=quantity,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    body: list[int],
    server_id: int,
    quantity: Union[Unset, QuantityEnum] = UNSET,
) -> Optional[
    Union[
        GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost,
        HTTPValidationError,
    ]
]:
    """Get Sales Speed By Gid

    Args:
        server_id (int):
        quantity (Union[Unset, QuantityEnum]):
        body (list[int]):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[GetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPostResponseGetSalesSpeedByGidItemPriceHistoryGetSalesSpeedPost, HTTPValidationError]
    """

    return (
        await asyncio_detailed(
            client=client,
            body=body,
            server_id=server_id,
            quantity=quantity,
        )
    ).parsed
