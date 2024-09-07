from com.ankama.dofus.server.game.protocol import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class NpcGenericActionRequest(_message.Message):
    __slots__ = ("npc_id", "npc_action_id", "npc_map_id")
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    NPC_ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    NPC_MAP_ID_FIELD_NUMBER: _ClassVar[int]
    npc_id: int
    npc_action_id: int
    npc_map_id: int
    def __init__(self, npc_id: _Optional[int] = ..., npc_action_id: _Optional[int] = ..., npc_map_id: _Optional[int] = ...) -> None: ...

class NpcDialogReplyRequest(_message.Message):
    __slots__ = ("reply_id",)
    REPLY_ID_FIELD_NUMBER: _ClassVar[int]
    reply_id: int
    def __init__(self, reply_id: _Optional[int] = ...) -> None: ...

class NpcsMapQuestStatusUpdateEvent(_message.Message):
    __slots__ = ("map_information",)
    class MapNpcQuest(_message.Message):
        __slots__ = ("map_id", "npcs_with_quests")
        class NpcWithQuest(_message.Message):
            __slots__ = ("npc_id", "quests_to_validate", "quests_to_start")
            NPC_ID_FIELD_NUMBER: _ClassVar[int]
            QUESTS_TO_VALIDATE_FIELD_NUMBER: _ClassVar[int]
            QUESTS_TO_START_FIELD_NUMBER: _ClassVar[int]
            npc_id: int
            quests_to_validate: _containers.RepeatedScalarFieldContainer[int]
            quests_to_start: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, npc_id: _Optional[int] = ..., quests_to_validate: _Optional[_Iterable[int]] = ..., quests_to_start: _Optional[_Iterable[int]] = ...) -> None: ...
        MAP_ID_FIELD_NUMBER: _ClassVar[int]
        NPCS_WITH_QUESTS_FIELD_NUMBER: _ClassVar[int]
        map_id: int
        npcs_with_quests: _containers.RepeatedCompositeFieldContainer[NpcsMapQuestStatusUpdateEvent.MapNpcQuest.NpcWithQuest]
        def __init__(self, map_id: _Optional[int] = ..., npcs_with_quests: _Optional[_Iterable[_Union[NpcsMapQuestStatusUpdateEvent.MapNpcQuest.NpcWithQuest, _Mapping]]] = ...) -> None: ...
    MAP_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    map_information: _containers.RepeatedCompositeFieldContainer[NpcsMapQuestStatusUpdateEvent.MapNpcQuest]
    def __init__(self, map_information: _Optional[_Iterable[_Union[NpcsMapQuestStatusUpdateEvent.MapNpcQuest, _Mapping]]] = ...) -> None: ...

class NpcGenericActionFailureEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class NpcDialogCreationEvent(_message.Message):
    __slots__ = ("map_id", "npc_id", "portal_type")
    class PortalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSUPPORTED: _ClassVar[NpcDialogCreationEvent.PortalType]
        ENUTROSOR: _ClassVar[NpcDialogCreationEvent.PortalType]
        SRAMBAD: _ClassVar[NpcDialogCreationEvent.PortalType]
        XELORIUM: _ClassVar[NpcDialogCreationEvent.PortalType]
        ECAFLIPUS: _ClassVar[NpcDialogCreationEvent.PortalType]
    UNSUPPORTED: NpcDialogCreationEvent.PortalType
    ENUTROSOR: NpcDialogCreationEvent.PortalType
    SRAMBAD: NpcDialogCreationEvent.PortalType
    XELORIUM: NpcDialogCreationEvent.PortalType
    ECAFLIPUS: NpcDialogCreationEvent.PortalType
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    PORTAL_TYPE_FIELD_NUMBER: _ClassVar[int]
    map_id: int
    npc_id: int
    portal_type: NpcDialogCreationEvent.PortalType
    def __init__(self, map_id: _Optional[int] = ..., npc_id: _Optional[int] = ..., portal_type: _Optional[_Union[NpcDialogCreationEvent.PortalType, str]] = ...) -> None: ...

class NpcDialogQuestionEvent(_message.Message):
    __slots__ = ("message_id", "dialog_params", "visible_replies")
    class VisibleReply(_message.Message):
        __slots__ = ("reply_id", "actions")
        class ActionInformation(_message.Message):
            __slots__ = ("id", "is_repeatable")
            ID_FIELD_NUMBER: _ClassVar[int]
            IS_REPEATABLE_FIELD_NUMBER: _ClassVar[int]
            id: int
            is_repeatable: bool
            def __init__(self, id: _Optional[int] = ..., is_repeatable: bool = ...) -> None: ...
        REPLY_ID_FIELD_NUMBER: _ClassVar[int]
        ACTIONS_FIELD_NUMBER: _ClassVar[int]
        reply_id: int
        actions: _containers.RepeatedCompositeFieldContainer[NpcDialogQuestionEvent.VisibleReply.ActionInformation]
        def __init__(self, reply_id: _Optional[int] = ..., actions: _Optional[_Iterable[_Union[NpcDialogQuestionEvent.VisibleReply.ActionInformation, _Mapping]]] = ...) -> None: ...
    MESSAGE_ID_FIELD_NUMBER: _ClassVar[int]
    DIALOG_PARAMS_FIELD_NUMBER: _ClassVar[int]
    VISIBLE_REPLIES_FIELD_NUMBER: _ClassVar[int]
    message_id: int
    dialog_params: _containers.RepeatedScalarFieldContainer[str]
    visible_replies: _containers.RepeatedCompositeFieldContainer[NpcDialogQuestionEvent.VisibleReply]
    def __init__(self, message_id: _Optional[int] = ..., dialog_params: _Optional[_Iterable[str]] = ..., visible_replies: _Optional[_Iterable[_Union[NpcDialogQuestionEvent.VisibleReply, _Mapping]]] = ...) -> None: ...

class TaxCollectorDialogQuestionEvent(_message.Message):
    __slots__ = ("alliance_information", "max_pods", "prospecting", "tax_collectors_count", "possible_attack", "looted_pods", "looted_items_value")
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    MAX_PODS_FIELD_NUMBER: _ClassVar[int]
    PROSPECTING_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTORS_COUNT_FIELD_NUMBER: _ClassVar[int]
    POSSIBLE_ATTACK_FIELD_NUMBER: _ClassVar[int]
    LOOTED_PODS_FIELD_NUMBER: _ClassVar[int]
    LOOTED_ITEMS_VALUE_FIELD_NUMBER: _ClassVar[int]
    alliance_information: _common_pb2.AllianceInformation
    max_pods: int
    prospecting: int
    tax_collectors_count: int
    possible_attack: int
    looted_pods: int
    looted_items_value: int
    def __init__(self, alliance_information: _Optional[_Union[_common_pb2.AllianceInformation, _Mapping]] = ..., max_pods: _Optional[int] = ..., prospecting: _Optional[int] = ..., tax_collectors_count: _Optional[int] = ..., possible_attack: _Optional[int] = ..., looted_pods: _Optional[int] = ..., looted_items_value: _Optional[int] = ...) -> None: ...

class PrismDialogQuestionEvent(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class EntityTalkEvent(_message.Message):
    __slots__ = ("entity_id", "text_id", "parameters")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    TEXT_ID_FIELD_NUMBER: _ClassVar[int]
    PARAMETERS_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    text_id: int
    parameters: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, entity_id: _Optional[int] = ..., text_id: _Optional[int] = ..., parameters: _Optional[_Iterable[str]] = ...) -> None: ...

class PlaySpellScriptOnNpcEvent(_message.Message):
    __slots__ = ("npc_id", "script_id")
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    SCRIPT_ID_FIELD_NUMBER: _ClassVar[int]
    npc_id: int
    script_id: int
    def __init__(self, npc_id: _Optional[int] = ..., script_id: _Optional[int] = ...) -> None: ...

class PlayAnimationOnNpcEvent(_message.Message):
    __slots__ = ("npc_id", "animation")
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    ANIMATION_FIELD_NUMBER: _ClassVar[int]
    npc_id: int
    animation: str
    def __init__(self, npc_id: _Optional[int] = ..., animation: _Optional[str] = ...) -> None: ...

class PlayEmoteOnNpcEvent(_message.Message):
    __slots__ = ("npc_id", "emote_id")
    NPC_ID_FIELD_NUMBER: _ClassVar[int]
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    npc_id: int
    emote_id: int
    def __init__(self, npc_id: _Optional[int] = ..., emote_id: _Optional[int] = ...) -> None: ...
