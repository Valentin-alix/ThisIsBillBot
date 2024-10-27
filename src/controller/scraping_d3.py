from typing import Any, Callable

from httpx import Timeout

from scraping_d3_client.scraping_d3_client.api.default import (
    create_character_character_post,
    get_mule_accept_bank_ids_character_mule_accept_bank_ids_get,
    patch_character_action_character_id_action_patch,
)
from scraping_d3_client.scraping_d3_client.client import Client
from scraping_d3_client.scraping_d3_client.models.character_action_enum import (
    CharacterActionEnum,
)
from scraping_d3_client.scraping_d3_client.models.character_create_schema import (
    CharacterCreateSchema,
)
from scraping_d3_client.scraping_d3_client.models.http_validation_error import (
    HTTPValidationError,
)
from src.const import BACKEND_URL
from src.controller.request_executor import RequestExecutor

SCRAPING_D3_CLIENT = Client(base_url=BACKEND_URL, timeout=Timeout(timeout=3))
request_executor = RequestExecutor()


class ScrapingD3Controller:
    @staticmethod
    def create_character(character_id: int, server_id: int):
        request_executor.run_with_callback(
            lambda: create_character_character_post.sync(
                client=SCRAPING_D3_CLIENT,
                body=CharacterCreateSchema(id=character_id, server_id=server_id),
            )
        )

    @staticmethod
    def patch_character_action(character_id: int, action: CharacterActionEnum | None):
        request_executor.run_with_callback(
            lambda: patch_character_action_character_id_action_patch.sync(
                id=character_id, client=SCRAPING_D3_CLIENT, action=action
            )
        )

    @staticmethod
    def get_mule_bank_ids(server_id: int, callback: Callable[[list[int]], Any]):
        def _callback(res: HTTPValidationError | list[int] | None):
            if isinstance(res, list):
                return callback(res)
            return callback([])

        request_executor.run_with_callback(
            lambda: get_mule_accept_bank_ids_character_mule_accept_bank_ids_get.sync(
                client=SCRAPING_D3_CLIENT, server_id=server_id
            ),
            callback=_callback,
        )
