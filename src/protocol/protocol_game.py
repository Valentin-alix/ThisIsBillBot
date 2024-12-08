import datetime
import json
import traceback
from collections.abc import Callable, Mapping
from functools import cache
from pathlib import Path
from typing import Any

from consts import GAME_MAPPINGS_JSON_FILE
from datas.protos.non_obf.game.game_message_pb2 import GameMessage
from google.protobuf import descriptor_pool
from google.protobuf.any_pb2 import Any as protoAny
from google.protobuf.descriptor import Descriptor, FieldDescriptor
from google.protobuf.json_format import MessageToDict
from google.protobuf.message import Message
from google.protobuf.message_factory import GetMessageClass

from src.controller.instancied_msg_info_controller import (
    InstanciedMessageInfoController,
)
from src.protocol.message import MessageInfo
from src.utils.type_guards import to_str_object_dict

TYPE_URL_PREFIX = "type.ankama.com/"
_GAME_MAPPINGS_PATH = Path(GAME_MAPPINGS_JSON_FILE)

POOL: descriptor_pool.DescriptorPool = descriptor_pool.Default()
FieldMappingToReal = Mapping[str, str | None]
FieldMappingToObf = Mapping[str, str]
RawGameMappings = dict[str, object]
ProtoToRealMapping = Mapping[str, tuple[str, FieldMappingToReal]]
ProtoToObfMapping = Mapping[str, tuple[str, FieldMappingToObf]]
MessageTransformer = Callable[[Message], Message]


def _get_mapping_info(mapping_value: Any) -> dict[str, object]:
    typed_mapping = to_str_object_dict(mapping_value)
    if typed_mapping is None:
        raise TypeError("Invalid mapping info")
    return typed_mapping


def _get_mapping_namespace(mapping_info: dict[str, object]) -> str:
    namespace = mapping_info["obf_msg_namespace"]
    if not isinstance(namespace, str):
        raise TypeError("Invalid obfuscated namespace")
    return namespace


def _get_field_mapping_to_real(
    mapping_info: dict[str, object],
) -> dict[str, str | None]:
    raw_field_mapping = mapping_info["field_mapping"]
    typed_raw_field_mapping = to_str_object_dict(raw_field_mapping)
    if typed_raw_field_mapping is None:
        raise TypeError("Invalid field mapping")

    field_mapping: dict[str, str | None] = {}
    for raw_key_obj, raw_value_obj in typed_raw_field_mapping.items():
        if raw_value_obj is not None and not isinstance(raw_value_obj, str):
            raise TypeError("Invalid field mapping value")
        field_mapping[raw_key_obj] = raw_value_obj
    return field_mapping


def _is_repeated_field(field_descriptor: FieldDescriptor) -> bool:
    return getattr(field_descriptor, "label") == FieldDescriptor.LABEL_REPEATED


@cache
def _load_game_mappings() -> RawGameMappings:
    with open(_GAME_MAPPINGS_PATH) as f:
        raw_mappings: object = json.load(f)
    typed_mappings = to_str_object_dict(raw_mappings)
    if typed_mappings is None:
        raise TypeError("Invalid game mappings payload")
    return typed_mappings


def get_mapping_proto_to_real() -> ProtoToRealMapping:
    return {
        _get_mapping_namespace(info): (
            clear_namespace[1:],
            _get_field_mapping_to_real(info),
        )
        for clear_namespace, raw_info in _load_game_mappings().items()
        for info in [_get_mapping_info(raw_info)]
    }


def get_mapping_proto_to_obf() -> ProtoToObfMapping:
    return {
        clear_namespace[1:]: (
            _get_mapping_namespace(info),
            {
                clear_field: obf_field
                for obf_field, clear_field in _get_field_mapping_to_real(info).items()
                if clear_field is not None
            },
        )
        for clear_namespace, raw_info in _load_game_mappings().items()
        for info in [_get_mapping_info(raw_info)]
    }


def is_usable_msg(msg_name: str) -> bool:
    return msg_name in get_mapping_proto_to_obf()


def get_obf_game_msg_info(
    content: bytes, from_server: bool, do_dump_values: bool
) -> MessageInfo:
    SHOW_URL = True

    received_msg_time = datetime.datetime.now()

    obf_game_type_url, _ = get_mapping_proto_to_obf()[GameMessage.DESCRIPTOR.full_name]
    game_msg_type = GetMessageClass(POOL.FindMessageTypeByName(obf_game_type_url))

    game_msg = game_msg_type()
    game_msg.ParseFromString(content)
    InstanciedMessageInfoController().add_msg(game_msg, True)

    msg_json = MessageToDict(
        game_msg,
        always_print_fields_with_no_presence=True,
        preserving_proto_field_name=True,
    )
    if SHOW_URL:
        root_oneof = game_msg.DESCRIPTOR.oneofs[0].name
        field_name = game_msg.WhichOneof(root_oneof)
        root_msg: Message = getattr(game_msg, field_name)

        root_msg_any_field: protoAny | None = None
        for _, field_value in root_msg.ListFields():
            if field_value.__class__ == protoAny:
                root_msg_any_field = field_value
                break

        if root_msg_any_field is None:
            raise ValueError("Did not found any in root msg")

        type_url = root_msg_any_field.type_url.split("/")[-1]

        sub_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(type_url)
        sub_msg_type = GetMessageClass(sub_msg_descriptor)

        sub_msg_content_unpacked: Message = sub_msg_type()
        root_msg_any_field.Unpack(sub_msg_content_unpacked)

        if do_dump_values:
            InstanciedMessageInfoController().add_msg(
                sub_msg_content_unpacked, from_server
            )
    else:
        type_url = game_msg.__class__.__name__

    return MessageInfo(
        received_time=received_msg_time,
        from_server=from_server,
        obf_msg_json=msg_json,
        sub_msg_name=type_url,
    )


def get_game_msg(
    content: bytes, do_dump_values: bool
) -> tuple[str, Message | None, Message, int]:
    obf_game_type_url, obf_game_field_mapping = get_mapping_proto_to_obf()[
        GameMessage.DESCRIPTOR.full_name
    ]
    uid_value = -1
    msg_descriptor: Descriptor = POOL.FindMessageTypeByName(obf_game_type_url)
    msg_type = GetMessageClass(msg_descriptor)

    msg = msg_type()
    msg.ParseFromString(content)

    if do_dump_values:
        InstanciedMessageInfoController().add_msg(msg, True)

    msg_one_of = next(
        obf_field
        for obf_field in obf_game_field_mapping.values()
        if msg.HasField(obf_field)
    )
    root_msg: Message = getattr(msg, msg_one_of)
    root_msg_any_field: protoAny | None = None

    root_msg_namespace = get_mapping_proto_to_real()[root_msg.DESCRIPTOR.full_name][0]

    for _, field_value in root_msg.ListFields():
        if field_value.__class__ == protoAny:
            root_msg_any_field = field_value
        else:
            uid_value = field_value

    if root_msg_any_field is None:
        raise ValueError("Did not found any in root msg")

    type_url = root_msg_any_field.type_url.split("/")[-1]
    sub_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(type_url)
    sub_msg_type = GetMessageClass(sub_msg_descriptor)

    sub_msg_content_unpacked: Message = sub_msg_type()
    root_msg_any_field.Unpack(sub_msg_content_unpacked)

    try:
        clear_sub_msg = get_clear_msg_from_obf(sub_msg_content_unpacked)
    except Exception:
        print(traceback.format_exc())
        clear_sub_msg = None

    return root_msg_namespace, clear_sub_msg, sub_msg_content_unpacked, uid_value


def get_game_msg_info(
    clear_sub_msg: Message | None,
    obf_sub_msg: Message,
    uid_value: int | None,
    from_server: bool,
    do_dump_values: bool = False,
) -> MessageInfo:
    received_msg_time = datetime.datetime.now()

    if do_dump_values:
        InstanciedMessageInfoController().add_msg(obf_sub_msg, from_server)

    if clear_sub_msg is not None:
        msg_json = MessageToDict(
            clear_sub_msg,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        )
        sub_msg_info = (clear_sub_msg, clear_sub_msg.DESCRIPTOR.full_name)
    else:
        msg_json = None
        sub_msg_info = (obf_sub_msg, obf_sub_msg.DESCRIPTOR.full_name)

    if msg_json and uid_value is not None:
        msg_json["uid"] = uid_value

    return MessageInfo(
        received_time=received_msg_time,
        from_server=from_server,
        msg_json=msg_json,
        sub_msg_name=f"{obf_sub_msg.DESCRIPTOR.full_name} -> {sub_msg_info[0].__class__.__name__}",
        obf_msg_json=MessageToDict(
            obf_sub_msg,
            always_print_fields_with_no_presence=True,
            preserving_proto_field_name=True,
        ),
    )


def get_obf_game_message_from_msg(
    root_msg_namespace: str, clear_sub_msg: Message, uid: int | None = None
) -> tuple[Message, Message] | None:
    obf_any_msg = protoAny()
    obf_msg = get_obf_msg_from_clear(clear_sub_msg)
    if obf_msg is None:
        return print(f"No mapping found for {clear_sub_msg.DESCRIPTOR.full_name}")

    obf_any_msg.Pack(obf_msg, type_url_prefix=TYPE_URL_PREFIX)
    obf_any_msg.type_url = (
        TYPE_URL_PREFIX
        + get_mapping_proto_to_obf()[clear_sub_msg.DESCRIPTOR.full_name][0]
    )

    obf_sub_type_url, obf_sub_field_mapping = get_mapping_proto_to_obf()[
        root_msg_namespace
    ]
    obf_sub_msg_type = GetMessageClass(POOL.FindMessageTypeByName(obf_sub_type_url))
    sub_msg_values: dict[str, Message | int] = {
        obf_sub_field_mapping["content"]: obf_any_msg
    }
    if "uid" in obf_sub_field_mapping:
        sub_msg_values[obf_sub_field_mapping["uid"]] = uid or -1
    obf_sub_msg = obf_sub_msg_type(**sub_msg_values)

    obf_game_type_url, obf_game_field_mapping = get_mapping_proto_to_obf()[
        GameMessage.DESCRIPTOR.full_name
    ]
    game_content_field_name = root_msg_namespace.split(".")[-1].lower()
    obf_game_msg_type = GetMessageClass(POOL.FindMessageTypeByName(obf_game_type_url))
    obf_game_msg = obf_game_msg_type(
        **{obf_game_field_mapping[game_content_field_name]: obf_sub_msg}
    )

    return obf_game_msg, obf_sub_msg


def get_clear_msg_from_obf(
    obf_msg: Message,
) -> Message | None:
    transformer = get_msg_transformer_to_clear(obf_msg.DESCRIPTOR.full_name)
    return transformer(obf_msg) if transformer else None


def get_obf_msg_from_clear(
    clear_msg: Message,
) -> Message | None:
    transformer = get_msg_transformer_to_obf(clear_msg.DESCRIPTOR.full_name)
    return transformer(clear_msg) if transformer else None


def get_msg_transformer_to_obf(msg_full_name: str):
    return get_msg_transformer(msg_full_name, get_mapping_proto_to_obf())


def get_msg_transformer_to_clear(msg_full_name: str):
    return get_msg_transformer(msg_full_name, get_mapping_proto_to_real())


def get_msg_transformer(
    msg_full_name: str,
    msg_mappings: ProtoToRealMapping | ProtoToObfMapping,
) -> MessageTransformer | None:
    related_mapping = msg_mappings.get(msg_full_name)
    if not related_mapping:
        return None

    output_msg_name, field_mapping = related_mapping

    try:
        output_msg_descriptor: Descriptor = POOL.FindMessageTypeByName(output_msg_name)
    except KeyError:
        return None
    output_msg_type = GetMessageClass(output_msg_descriptor)

    def transformer(msg: Message) -> Message:
        output_msg = output_msg_type()
        for msg_field, msg_field_value in msg.ListFields():
            output_msg_field_name = field_mapping.get(msg_field.name)
            if output_msg_field_name is None:
                continue
            try:
                set_field_from_mapping_field(
                    msg_field,
                    msg_field_value,
                    output_msg,
                    output_msg_field_name,
                    msg_mappings,
                )
            except (AttributeError, ValueError, OverflowError):
                pass
        return output_msg

    return transformer


def set_field_from_mapping_field(
    msg_field: FieldDescriptor,
    msg_field_value: Any,
    output_msg: Message,
    output_msg_field_name: str,
    msg_mappings: ProtoToRealMapping | ProtoToObfMapping,
) -> None:
    if _is_repeated_field(msg_field):
        output_field_value = getattr(output_msg, output_msg_field_name)
        is_map_field = (
            msg_field.message_type and msg_field.message_type.GetOptions().map_entry
        )
        if msg_field.type == FieldDescriptor.TYPE_MESSAGE:
            for sub_msg_value in msg_field_value:
                sub_msg_value: Message
                sub_transformer = get_msg_transformer(
                    sub_msg_value.DESCRIPTOR.full_name, msg_mappings
                )
                if not sub_transformer:
                    continue
                sub_output_msg = sub_transformer(
                    msg_field_value[sub_msg_value] if is_map_field else sub_msg_value
                )
                if sub_output_msg is None:
                    continue
                if is_map_field:
                    output_field_value[sub_msg_value].CopyFrom(sub_output_msg)
                else:
                    output_field_value.append(sub_output_msg)
        else:
            if is_map_field:
                output_field_value.MergeFrom(msg_field_value)
            else:
                output_field_value.extend(msg_field_value)

    elif msg_field.type == FieldDescriptor.TYPE_MESSAGE:
        if not isinstance(msg_field_value, Message):
            return
        output_field_value = getattr(output_msg, output_msg_field_name)

        sub_transformer = get_msg_transformer(
            msg_field_value.DESCRIPTOR.full_name, msg_mappings
        )
        if sub_transformer is not None:
            try:
                output_field_value.CopyFrom(sub_transformer(msg_field_value))
            except TypeError:
                pass

    else:
        setattr(output_msg, output_msg_field_name, msg_field_value)
