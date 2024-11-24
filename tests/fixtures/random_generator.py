import datetime
import random

from d3_database.data_center.data_reader import DataReader
from d3_database.data_center.i18n import I18N
from src.protocol.message import MessageInfo
from ProtoMapperAssembly.data.non_obf.protos.game.common_pb2 import (
    ObjectItem,
    ObjectItemInventory,
)
from src.core.bot.bot_factory import BotFactory
from src.core.signals.shared_farm_signals import SharedSignals
from src.services.logging.logger import Logger


def generate_random_message_info() -> MessageInfo:
    return MessageInfo(
        received_time=datetime.datetime.now()
        - datetime.timedelta(seconds=random.randint(0, 3600)),
        from_server=random.choice([True, False]),
        sub_msg_name=random.choice(
            [
                "MapEntered",
                "MovementConfirmed",
                "CastSpell",
                "ItemDropped",
                "CharacterStats",
                "ChatMessage",
                "FightStarted",
                "FightEnded",
                "NPCInteracted",
                "InventoryUpdated",
            ]
        ),
        obf_msg_json={
            "field_" + str(i): random.choice([random.randint(0, 1000), "data", True])
            for i in range(random.randint(20, 50))
        },
        msg_json={
            "action": random.choice(["move", "cast", "pickup", "drop"]),
            "value": random.randint(0, 1000),
            "timestamp": datetime.datetime.now().isoformat(),
        },
    )


def generate_random_messages(count: int) -> list[MessageInfo]:
    return [generate_random_message_info() for _ in range(count)]


def generate_random_bot():
    login = f"CertUser{random.randint(1, 10_000)}"
    return BotFactory.create_bot(
        SharedSignals(),
        account={
            "apikeyFile": "/path/to/apikey/file.json",
            "apikey": {
                "key": "A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p6",
                "provider": "ankama",
                "refreshToken": "X1Y2Z3A4B5C6D7E8F9G0H1I2J3K4L5M6N7O8P9Q0R1S2T3U4V5W6X7Y8Z9",
                "isStayLoggedIn": True,
                "accountId": 482395,
                "login": login,
                "certificate": {
                    "id": 4321,
                    "encodedCertificate": "ABCD1234EFGH5678IJKL9012MNOP3456QRST7890UVWX1234YZAB5678CDEF9012",
                    "login": login,
                },
                "refreshDate": 1762825632,
            },
        },
        is_fake=True,
    )


def generate_random_log(logger: Logger) -> None:
    """Émet `count` logs aléatoires couvrant tous les niveaux.

    Parameters
    - logger: instance de `src.common.logger.Logger`
    - count: nombre de logs à générer
    """
    import traceback

    levels = ["debug", "info", "warning", "error", "critical"]

    templates = [
        "User {user} performed action {action} on resource {res}",
        "Processed {n} items in {ms}ms",
        "Connection from {ip} established",
        "Failed to process item {id}: {reason}",
        "Background job {job} completed successfully",
        "Received unexpected payload: {payload}",
        "Cache miss for key {key}",
        "Permission denied for user {user} on {res}",
        "External API returned status {status} for {endpoint}",
        "Metric: {metric}={value}",
    ]

    lvl = random.choice(levels)
    tpl = random.choice(templates)
    payload = {
        "user": f"user{random.randint(1, 1000)}",
        "action": random.choice(["login", "logout", "buy", "sell", "update"]),
        "res": random.choice(["inventory", "profile", "map", "bank"]),
        "n": random.randint(1, 5000),
        "ms": random.randint(1, 2000),
        "ip": f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}",
        "id": random.randint(1, 100000),
        "reason": random.choice(["timeout", "invalid_data", "missing_field"]),
        "job": random.choice(["sync", "scrape", "cleanup"]),
        "payload": {
            "k": random.randint(0, 10),
            "v": random.choice([True, False, "x"]),
        },
        "key": f"k{random.randint(1, 100)}",
        "endpoint": random.choice(["/items", "/login", "/price"]),
        "status": random.choice([200, 201, 400, 401, 500]),
        "metric": random.choice(["cpu", "mem", "latency"]),
        "value": round(random.random() * 100, 2),
    }

    # ensure complex fields are rendered as readable strings (no raw dicts)
    payload_for_format = payload.copy()
    if isinstance(payload_for_format.get("payload"), dict):
        try:
            import json

            payload_for_format["payload"] = json.dumps(
                payload_for_format["payload"], separators=(",", ":")
            )
        except Exception:
            payload_for_format["payload"] = str(payload_for_format["payload"])

    try:
        msg_text = tpl.format(**payload_for_format)
    except Exception:
        # fallback: produce a human readable sentence from keys
        parts = [f"{k}={v}" for k, v in payload_for_format.items()]
        msg_text = " ".join(parts)

    if lvl == "error" and random.random() < 0.25:
        try:
            raise RuntimeError(f"Simulated error for {payload.get('id')}")
        except Exception:
            tb = traceback.format_exc()
            logger.error(f"{msg_text}\n{tb}")
            return

    if lvl == "debug":
        logger.debug(msg_text)
    elif lvl == "info":
        logger.info(msg_text)
    elif lvl == "warning":
        logger.warning(msg_text)
    elif lvl == "error":
        logger.error(msg_text)
    elif lvl == "critical":
        logger.critical(msg_text)


def generate_random_item() -> ObjectItemInventory:
    return ObjectItemInventory(
        position=random.randint(0, 63),
        item=ObjectItem(
            uid=random.randint(1, 10_000),
            quantity=random.randint(1, 100),
            gid=random.choice(
                list(
                    item.id
                    for item in DataReader().item_by_id.values()
                    if item.nameId in I18N().name_by_id
                )
            ),
        ),
    )


def generate_random_inventory() -> dict[int, ObjectItemInventory]:
    inventory: dict[int, ObjectItemInventory] = {}
    for _ in range(random.randint(25, 100)):
        object_item_inventory = generate_random_item()
        inventory[object_item_inventory.item.gid] = object_item_inventory
    return inventory
