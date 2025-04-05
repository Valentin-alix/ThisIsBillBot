import os
from threading import RLock

import msgspec
from datas.protos.non_obf.game.common_pb2 import (
    ActorPositionInformation,
)
from dofus_unity_reader.data_center.data_reader import DataReader
from dofus_unity_reader.data_center.i18n import I18N
from python_utils.singleton import Singleton

from src.const import RESOURCE_FOLDER
from src.services.logging_utils.loggers import BotLogger


class ForbiddenMonsterController(metaclass=Singleton):
    _LOCK = RLock()
    _FILE_PATH = os.path.join(RESOURCE_FOLDER, "forbidden_monster_race.json")
    _DEFEAT_THRESHOLD = 6

    def __init__(self) -> None:
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        if not os.path.exists(self._FILE_PATH):
            default_data: dict[str, dict[str, int]] = {"defeat_count_by_name": {}}
            with open(self._FILE_PATH, "wb+") as file:
                file.write(msgspec.json.encode(default_data))

    def _load_data(self) -> dict[str, int]:
        with open(self._FILE_PATH, "rb") as file:
            data = msgspec.json.decode(file.read())
            return data.get("defeat_count_by_name", {})

    def _save_data(self, defeat_count_by_name: dict[str, int]) -> None:
        with open(self._FILE_PATH, "wb") as file:
            file.write(
                msgspec.json.encode({"defeat_count_by_name": defeat_count_by_name})
            )

    def increment_defeat_count(self, name_id: int, logger: BotLogger) -> None:
        with self._LOCK:
            self._ensure_file_exists()
            defeat_count_by_name = self._load_data()
            monster_name = I18N().name_by_id[name_id]
            current_count = defeat_count_by_name.get(monster_name, 0)
            new_count = current_count + 1
            defeat_count_by_name[monster_name] = new_count
            self._save_data(defeat_count_by_name)

            if new_count >= self._DEFEAT_THRESHOLD:
                logger.warning(
                    f"Monster name_id {name_id} reached {new_count} defeats, now forbidden"
                )
            else:
                logger.info(
                    f"Monster name_id {name_id} defeat count: {new_count}/{self._DEFEAT_THRESHOLD}"
                )

    def reset_defeat_count(self, name_id: int, logger: BotLogger) -> None:
        with self._LOCK:
            self._ensure_file_exists()
            defeat_count_by_name = self._load_data()
            monster_name = I18N().name_by_id[name_id]
            if monster_name in defeat_count_by_name:
                del defeat_count_by_name[monster_name]
                self._save_data(defeat_count_by_name)
                logger.info(f"Monster {monster_name} defeat count reset after victory")

    def is_group_allowed(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> bool:
        with self._LOCK:
            self._ensure_file_exists()
            defeat_count_by_name = self._load_data()
            main_creature_name = I18N().name_by_id[
                DataReader()
                .monsters_by_id[monster_group.identification.main_creature.gid]
                .nameId
            ]
            if (
                defeat_count_by_name.get(main_creature_name, 0)
                >= self._DEFEAT_THRESHOLD
            ):
                return False

            for underling in monster_group.identification.underlings:
                underling_name = I18N().name_by_id[
                    DataReader().monsters_by_id[underling.gid].nameId
                ]
                if (
                    defeat_count_by_name.get(underling_name, 0)
                    >= self._DEFEAT_THRESHOLD
                ):
                    return False

            return True

    def get_unique_name_id_from_group(
        self,
        monster_group: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor,
    ) -> int | None:
        name_ids = {
            DataReader()
            .monsters_by_id[monster_group.identification.main_creature.gid]
            .nameId
        }
        for underling in monster_group.identification.underlings:
            name_ids.add(DataReader().monsters_by_id[underling.gid].nameId)

        if len(name_ids) == 1:
            return next(iter(name_ids))
        return None
