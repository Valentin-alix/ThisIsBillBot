from http import HTTPStatus
from typing import Any, Optional, Union

import httpx

from ... import errors
from ...client import AuthenticatedClient, Client
from ...models.category_enum import CategoryEnum
from ...models.http_validation_error import HTTPValidationError
from ...models.item_type_schemas import ItemTypeSchemas
from ...types import UNSET, Response


def _get_kwargs(
    *,
    category: CategoryEnum,
) -> dict[str, Any]:
    params: dict[str, Any] = {}

    json_category = category.value
    params["category"] = json_category

    params = {k: v for k, v in params.items() if v is not UNSET and v is not None}

    _kwargs: dict[str, Any] = {
        "method": "get",
        "url": "/data_center/type_item",
        "params": params,
    }

    return _kwargs


def _parse_response(
    *, client: Union[AuthenticatedClient, Client], response: httpx.Response
) -> Optional[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    if response.status_code == 200:
        response_200 = []
        _response_200 = response.json()
        for response_200_item_data in _response_200:
            response_200_item = ItemTypeSchemas.from_dict(response_200_item_data)

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
) -> Response[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    return Response(
        status_code=HTTPStatus(response.status_code),
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(client=client, response=response),
    )


def sync_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    category: CategoryEnum,
) -> Response[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    """Get Type Items

    Args:
        category (CategoryEnum):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ItemTypeSchemas']]]
    """

    kwargs = _get_kwargs(
        category=category,
    )

    response = client.get_httpx_client().request(
        **kwargs,
    )

    return _build_response(client=client, response=response)


def sync(
    *,
    client: Union[AuthenticatedClient, Client],
    category: CategoryEnum,
) -> Optional[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    """Get Type Items

    Args:
        category (CategoryEnum):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ItemTypeSchemas']]
    """

    return sync_detailed(
        client=client,
        category=category,
    ).parsed


async def asyncio_detailed(
    *,
    client: Union[AuthenticatedClient, Client],
    category: CategoryEnum,
) -> Response[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    """Get Type Items

    Args:
        category (CategoryEnum):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Response[Union[HTTPValidationError, list['ItemTypeSchemas']]]
    """

    kwargs = _get_kwargs(
        category=category,
    )

    response = await client.get_async_httpx_client().request(**kwargs)

    return _build_response(client=client, response=response)


async def asyncio(
    *,
    client: Union[AuthenticatedClient, Client],
    category: CategoryEnum,
) -> Optional[Union[HTTPValidationError, list["ItemTypeSchemas"]]]:
    """Get Type Items

    Args:
        category (CategoryEnum):

    Raises:
        errors.UnexpectedStatus: If the server returns an undocumented status code and Client.raise_on_unexpected_status is True.
        httpx.TimeoutException: If the request takes longer than Client.timeout.

    Returns:
        Union[HTTPValidationError, list['ItemTypeSchemas']]
    """

    return (
        await asyncio_detailed(
            client=client,
            category=category,
        )
    ).parsed
