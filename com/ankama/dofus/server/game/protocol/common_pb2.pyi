from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DelayedActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISCONNECT: _ClassVar[DelayedActionType]
    OBJECT_USE: _ClassVar[DelayedActionType]
    JOIN_CHARACTER: _ClassVar[DelayedActionType]
    AGGRESSION_IMMUNE: _ClassVar[DelayedActionType]

class AllianceRelation(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ALLIANCE_RELATION_NONE: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_MINE: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_DEF: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_ATT: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_NEUTRAL: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_ALLY: _ClassVar[AllianceRelation]
    ALLIANCE_RELATION_ENEMY: _ClassVar[AllianceRelation]

class ChallengeMod(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHALLENGE_CHOICE: _ClassVar[ChallengeMod]
    CHALLENGE_RANDOM: _ClassVar[ChallengeMod]

class ChallengeBonus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHALLENGE_EXPERIENCE_BONUS: _ClassVar[ChallengeBonus]
    CHALLENGE_DROP_BONUS: _ClassVar[ChallengeBonus]

class CharacterState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NOT_CONNECTED: _ClassVar[CharacterState]
    IN_ROLE_PLAY: _ClassVar[CharacterState]
    IN_FIGHT: _ClassVar[CharacterState]
    UNKNOWN_STATE: _ClassVar[CharacterState]

class Alignment(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNKNOWN: _ClassVar[Alignment]
    WITHOUT: _ClassVar[Alignment]
    NEUTRAL: _ClassVar[Alignment]
    ANGEL: _ClassVar[Alignment]
    EVIL: _ClassVar[Alignment]

class Gender(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MALE: _ClassVar[Gender]
    FEMALE: _ClassVar[Gender]

class Hierarchy(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ROLE_UNAVAILABLE: _ClassVar[Hierarchy]
    ROLE_PLAYER: _ClassVar[Hierarchy]
    ROLE_MODERATOR: _ClassVar[Hierarchy]
    ROLE_GAME_MASTER_PADAWAN: _ClassVar[Hierarchy]
    ROLE_GAME_MASTER: _ClassVar[Hierarchy]
    ROLE_ADMIN: _ClassVar[Hierarchy]
    ROLE_UNKNOWN_SPECIAL_USER: _ClassVar[Hierarchy]

class AttackableStatus(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NON_ATTACKABLE: _ClassVar[AttackableStatus]
    PVP_ENABLED_ATTACKABLE: _ClassVar[AttackableStatus]
    PVP_ENABLED_NON_ATTACKABLE: _ClassVar[AttackableStatus]
    AVA_ENABLED_ATTACKABLE: _ClassVar[AttackableStatus]
    AVA_ENABLED_NON_ATTACKABLE: _ClassVar[AttackableStatus]
    AVA_DISQUALIFIED: _ClassVar[AttackableStatus]
    AVA_PREQUALIFIED_ATTACKABLE: _ClassVar[AttackableStatus]

class Restriction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CANNOT_BE_ATTACKED: _ClassVar[Restriction]
    CANNOT_BE_CHALLENGED: _ClassVar[Restriction]
    CANNOT_TRADE: _ClassVar[Restriction]
    CANNOT_BE_ATTACKED_BY_MUTANT: _ClassVar[Restriction]
    CANNOT_RUN: _ClassVar[Restriction]
    FORCE_SLOW_WALK: _ClassVar[Restriction]
    CANNOT_MINIMIZE: _ClassVar[Restriction]
    CANNOT_MOVE: _ClassVar[Restriction]
    CANNOT_ATTACK: _ClassVar[Restriction]
    CANNOT_CHALLENGE: _ClassVar[Restriction]
    CANNOT_EXCHANGE: _ClassVar[Restriction]
    CANNOT_ATTACK_AS_MUTANT: _ClassVar[Restriction]
    CANNOT_CHAT: _ClassVar[Restriction]
    CANNOT_USE_OBJECT: _ClassVar[Restriction]
    CANNOT_USE_TAX_COLLECTOR: _ClassVar[Restriction]
    CANNOT_USE_INTERACTIVE: _ClassVar[Restriction]
    CANNOT_SPEAK_TO_NPC: _ClassVar[Restriction]
    CANNOT_CHANGE_ZONE: _ClassVar[Restriction]
    CANNOT_ATTACK_MONSTER: _ClassVar[Restriction]

class DialogType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIALOG_BOOK: _ClassVar[DialogType]
    DIALOG_DIALOG: _ClassVar[DialogType]
    DIALOG_LOCKABLE: _ClassVar[DialogType]
    DIALOG_PURCHASABLE: _ClassVar[DialogType]
    DIALOG_GUILD_INVITATION: _ClassVar[DialogType]
    DIALOG_GUILD_CREATE: _ClassVar[DialogType]
    DIALOG_GUILD_RENAME: _ClassVar[DialogType]
    DIALOG_MARRIAGE: _ClassVar[DialogType]
    DIALOG_DUNGEON_MEETING: _ClassVar[DialogType]
    DIALOG_SPELL_FORGET: _ClassVar[DialogType]
    DIALOG_TELEPORTER: _ClassVar[DialogType]
    DIALOG_EXCHANGE: _ClassVar[DialogType]
    DIALOG_ALLIANCE_INVITATION: _ClassVar[DialogType]
    DIALOG_ALLIANCE_CREATE: _ClassVar[DialogType]
    DIALOG_ALLIANCE_RENAME: _ClassVar[DialogType]
    DIALOG_HAVENBAG_MEETING: _ClassVar[DialogType]

class ExchangeType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    NPC_SHOP: _ClassVar[ExchangeType]
    PLAYER_TRADE: _ClassVar[ExchangeType]
    NPC_TRADE: _ClassVar[ExchangeType]
    CRAFT: _ClassVar[ExchangeType]
    STORAGE: _ClassVar[ExchangeType]
    SHOP_STOCK: _ClassVar[ExchangeType]
    TAX_COLLECTOR: _ClassVar[ExchangeType]
    NPC_MODIFY_TRADE: _ClassVar[ExchangeType]
    BIDHOUSE_SELL: _ClassVar[ExchangeType]
    BIDHOUSE_BUY: _ClassVar[ExchangeType]
    MULTICRAFT_CRAFTER: _ClassVar[ExchangeType]
    MULTICRAFT_CUSTOMER: _ClassVar[ExchangeType]
    JOB_INDEX: _ClassVar[ExchangeType]
    MOUNT: _ClassVar[ExchangeType]
    MOUNT_STABLE: _ClassVar[ExchangeType]
    NPC_RESURECT_PET: _ClassVar[ExchangeType]
    NPC_TRADE_DRAGOTURKEY: _ClassVar[ExchangeType]
    REALESTATE_HOUSE: _ClassVar[ExchangeType]
    REALESTATE_FARM: _ClassVar[ExchangeType]
    RUNES_TRADE: _ClassVar[ExchangeType]
    RECYCLE_TRADE: _ClassVar[ExchangeType]
    BANK: _ClassVar[ExchangeType]
    TRASHBIN: _ClassVar[ExchangeType]
    ALLIANCE_PRISM: _ClassVar[ExchangeType]
    HAVENBAG: _ClassVar[ExchangeType]
    NPC_TRADE_SEEMYOOL: _ClassVar[ExchangeType]
    NPC_TRADE_RHINEETLE: _ClassVar[ExchangeType]
    EVOLUTIVE_OBJECT_ELEMENTARY_RECYCLE: _ClassVar[ExchangeType]
    NPC_RIDE_CAPABILITY_TRADE: _ClassVar[ExchangeType]
    GUILD_CHEST: _ClassVar[ExchangeType]

class FightType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIGHT_TYPE_CHALLENGE: _ClassVar[FightType]
    FIGHT_TYPE_AGGRESSION: _ClassVar[FightType]
    FIGHT_TYPE_PvMA: _ClassVar[FightType]
    FIGHT_TYPE_MXvM: _ClassVar[FightType]
    FIGHT_TYPE_PvM: _ClassVar[FightType]
    FIGHT_TYPE_PvT: _ClassVar[FightType]
    FIGHT_TYPE_PvMU: _ClassVar[FightType]
    FIGHT_TYPE_PVP_ARENA: _ClassVar[FightType]
    FIGHT_TYPE_KOH: _ClassVar[FightType]
    FIGHT_TYPE_PvPr: _ClassVar[FightType]
    FIGHT_TYPE_BREACH: _ClassVar[FightType]

class TeamType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEAM_TYPE_PLAYER: _ClassVar[TeamType]
    TEAM_TYPE_MONSTER: _ClassVar[TeamType]
    TEAM_TYPE_MUTANT: _ClassVar[TeamType]
    TEAM_TYPE_TAX_COLLECTOR: _ClassVar[TeamType]
    TEAM_TYPE_BAD_PLAYER: _ClassVar[TeamType]
    TEAM_TYPE_PRISM: _ClassVar[TeamType]

class FightOption(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    FIGHT_OPTION_SET_SECRET: _ClassVar[FightOption]
    FIGHT_OPTION_SET_TO_PARTY_ONLY: _ClassVar[FightOption]
    FIGHT_OPTION_SET_CLOSED: _ClassVar[FightOption]
    FIGHT_OPTION_ASK_FOR_HELP: _ClassVar[FightOption]

class FightOutcome(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    RESULT_LOST: _ClassVar[FightOutcome]
    RESULT_DRAW: _ClassVar[FightOutcome]
    RESULT_VICTORY: _ClassVar[FightOutcome]
    RESULT_TAX: _ClassVar[FightOutcome]
    RESULT_DEFENDER_GROUP: _ClassVar[FightOutcome]

class FightInvisibilityState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVISIBLE: _ClassVar[FightInvisibilityState]
    DETECTED: _ClassVar[FightInvisibilityState]
    VISIBLE: _ClassVar[FightInvisibilityState]

class Team(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    TEAM_CHALLENGER: _ClassVar[Team]
    TEAM_DEFENDER: _ClassVar[Team]
    TEAM_SPECTATOR: _ClassVar[Team]
    TEAM_NEUTRAL: _ClassVar[Team]

class ShortcutBar(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    GENERAL_SHORTCUT_BAR: _ClassVar[ShortcutBar]
    SPELL_SHORTCUT_BAR: _ClassVar[ShortcutBar]

class PresetType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    CHARACTER: _ClassVar[PresetType]
    FORGETTABLE_SPELL: _ClassVar[PresetType]

class Direction(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DIRECTION_EAST: _ClassVar[Direction]
    DIRECTION_SOUTH_EAST: _ClassVar[Direction]
    DIRECTION_SOUTH: _ClassVar[Direction]
    DIRECTION_SOUTH_WEST: _ClassVar[Direction]
    DIRECTION_WEST: _ClassVar[Direction]
    DIRECTION_NORTH_WEST: _ClassVar[Direction]
    DIRECTION_NORTH: _ClassVar[Direction]
    DIRECTION_NORTH_EAST: _ClassVar[Direction]

class ObjectError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVENTORY_FULL: _ClassVar[ObjectError]
    CANNOT_EQUIP_TWICE: _ClassVar[ObjectError]
    NOT_TRADABLE: _ClassVar[ObjectError]
    CANNOT_DROP: _ClassVar[ObjectError]
    CANNOT_DROP_NO_PLACE: _ClassVar[ObjectError]
    CANNOT_DESTROY: _ClassVar[ObjectError]
    LEVEL_TOO_LOW: _ClassVar[ObjectError]
    LIVING_OBJECT_REFUSED_FOOD: _ClassVar[ObjectError]
    CANNOT_UNEQUIP: _ClassVar[ObjectError]
    CANNOT_EQUIP_HERE: _ClassVar[ObjectError]
    CRITERIONS: _ClassVar[ObjectError]
    SYMBIOTIC_OBJECT_ERROR: _ClassVar[ObjectError]
    EVOLUTIVE_OBJECT_REFUSED_FOOD: _ClassVar[ObjectError]

class ObjectOrigin(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ORIGIN_UNDEFINED: _ClassVar[ObjectOrigin]
    ORIGIN_QUEST: _ClassVar[ObjectOrigin]

class SocialRecruitmentType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    DISABLED: _ClassVar[SocialRecruitmentType]
    AUTOMATIC: _ClassVar[SocialRecruitmentType]
    MANUAL: _ClassVar[SocialRecruitmentType]

class SocialApplicationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    APPLICATION_ADDED: _ClassVar[SocialApplicationState]
    APPLICATION_DELETED: _ClassVar[SocialApplicationState]
    APPLICATION_UPDATED: _ClassVar[SocialApplicationState]

class ServerType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    UNDEFINED: _ClassVar[ServerType]
    CLASSICAL: _ClassVar[ServerType]
    KOLIZEUM: _ClassVar[ServerType]
    TOURNAMENT: _ClassVar[ServerType]
    EPIC: _ClassVar[ServerType]
    TEMPORIS: _ClassVar[ServerType]

class SocialGroupOperationResult(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOCIAL_GROUP_OPERATION_OK: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_NAME_INVALID: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_ALREADY_IN_GROUP: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_NAME_ALREADY_EXISTS: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_LEAVE: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_CANCEL: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_REQUIREMENT_UNMET: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_EMBLEM_INVALID: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_TAG_INVALID: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_TAG_ALREADY_EXISTS: _ClassVar[SocialGroupOperationResult]
    SOCIAL_GROUP_ERROR_UNKNOWN: _ClassVar[SocialGroupOperationResult]

class SocialNoticeError(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOCIAL_NOTICE_UNKNOWN_ERROR: _ClassVar[SocialNoticeError]
    SOCIAL_NOTICE_INVALID_RIGHTS: _ClassVar[SocialNoticeError]
    SOCIAL_NOTICE_COOLDOWN: _ClassVar[SocialNoticeError]

class SocialGroupInvitationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    SOCIAL_GROUP_INVITATION_FAILED: _ClassVar[SocialGroupInvitationState]
    SOCIAL_GROUP_INVITATION_SENT: _ClassVar[SocialGroupInvitationState]
    SOCIAL_GROUP_INVITATION_CANCELED: _ClassVar[SocialGroupInvitationState]
    SOCIAL_GROUP_INVITATION_OK: _ClassVar[SocialGroupInvitationState]

class TaxCollectorState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    STATE_COLLECTING: _ClassVar[TaxCollectorState]
    STATE_WAITING_FOR_HELP: _ClassVar[TaxCollectorState]
    STATE_FIGHTING: _ClassVar[TaxCollectorState]

class MountCharacteristic(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ENERGY: _ClassVar[MountCharacteristic]
    SERENITY: _ClassVar[MountCharacteristic]
    STAMINA: _ClassVar[MountCharacteristic]
    LOVE: _ClassVar[MountCharacteristic]
    MATURITY: _ClassVar[MountCharacteristic]
    TIREDNESS: _ClassVar[MountCharacteristic]
    CARRIER: _ClassVar[MountCharacteristic]
    FERTILE: _ClassVar[MountCharacteristic]
    PREGNANT: _ClassVar[MountCharacteristic]

class SpellModifierActionType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    ACTION_INVALID: _ClassVar[SpellModifierActionType]
    ACTION_BOOST: _ClassVar[SpellModifierActionType]
    ACTION_REMOVE_BOOST: _ClassVar[SpellModifierActionType]
    ACTION_SET: _ClassVar[SpellModifierActionType]

class SpellModifierType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    INVALID_MODIFICATION: _ClassVar[SpellModifierType]
    RANGE: _ClassVar[SpellModifierType]
    DAMAGE: _ClassVar[SpellModifierType]
    BASE_DAMAGE: _ClassVar[SpellModifierType]
    HEAL_BONUS: _ClassVar[SpellModifierType]
    AP_COST: _ClassVar[SpellModifierType]
    CAST_INTERVAL: _ClassVar[SpellModifierType]
    CRITICAL_HIT_BONUS: _ClassVar[SpellModifierType]
    CAST_LINE: _ClassVar[SpellModifierType]
    LOS: _ClassVar[SpellModifierType]
    MAX_CAST_PER_TURN: _ClassVar[SpellModifierType]
    MAX_CAST_PER_TARGET: _ClassVar[SpellModifierType]
    RANGE_MAX: _ClassVar[SpellModifierType]
    RANGE_MIN: _ClassVar[SpellModifierType]
    OCCUPIED_CELL: _ClassVar[SpellModifierType]
    FREE_CELL: _ClassVar[SpellModifierType]
    VISIBLE_TARGET: _ClassVar[SpellModifierType]
    PORTAL_FREE_CELL: _ClassVar[SpellModifierType]
    PORTAL_PROJECTION: _ClassVar[SpellModifierType]

class RealEstateOrder(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    PRICE_ASC: _ClassVar[RealEstateOrder]
    PRICE_DSC: _ClassVar[RealEstateOrder]
DISCONNECT: DelayedActionType
OBJECT_USE: DelayedActionType
JOIN_CHARACTER: DelayedActionType
AGGRESSION_IMMUNE: DelayedActionType
ALLIANCE_RELATION_NONE: AllianceRelation
ALLIANCE_RELATION_MINE: AllianceRelation
ALLIANCE_RELATION_DEF: AllianceRelation
ALLIANCE_RELATION_ATT: AllianceRelation
ALLIANCE_RELATION_NEUTRAL: AllianceRelation
ALLIANCE_RELATION_ALLY: AllianceRelation
ALLIANCE_RELATION_ENEMY: AllianceRelation
CHALLENGE_CHOICE: ChallengeMod
CHALLENGE_RANDOM: ChallengeMod
CHALLENGE_EXPERIENCE_BONUS: ChallengeBonus
CHALLENGE_DROP_BONUS: ChallengeBonus
NOT_CONNECTED: CharacterState
IN_ROLE_PLAY: CharacterState
IN_FIGHT: CharacterState
UNKNOWN_STATE: CharacterState
UNKNOWN: Alignment
WITHOUT: Alignment
NEUTRAL: Alignment
ANGEL: Alignment
EVIL: Alignment
MALE: Gender
FEMALE: Gender
ROLE_UNAVAILABLE: Hierarchy
ROLE_PLAYER: Hierarchy
ROLE_MODERATOR: Hierarchy
ROLE_GAME_MASTER_PADAWAN: Hierarchy
ROLE_GAME_MASTER: Hierarchy
ROLE_ADMIN: Hierarchy
ROLE_UNKNOWN_SPECIAL_USER: Hierarchy
NON_ATTACKABLE: AttackableStatus
PVP_ENABLED_ATTACKABLE: AttackableStatus
PVP_ENABLED_NON_ATTACKABLE: AttackableStatus
AVA_ENABLED_ATTACKABLE: AttackableStatus
AVA_ENABLED_NON_ATTACKABLE: AttackableStatus
AVA_DISQUALIFIED: AttackableStatus
AVA_PREQUALIFIED_ATTACKABLE: AttackableStatus
CANNOT_BE_ATTACKED: Restriction
CANNOT_BE_CHALLENGED: Restriction
CANNOT_TRADE: Restriction
CANNOT_BE_ATTACKED_BY_MUTANT: Restriction
CANNOT_RUN: Restriction
FORCE_SLOW_WALK: Restriction
CANNOT_MINIMIZE: Restriction
CANNOT_MOVE: Restriction
CANNOT_ATTACK: Restriction
CANNOT_CHALLENGE: Restriction
CANNOT_EXCHANGE: Restriction
CANNOT_ATTACK_AS_MUTANT: Restriction
CANNOT_CHAT: Restriction
CANNOT_USE_OBJECT: Restriction
CANNOT_USE_TAX_COLLECTOR: Restriction
CANNOT_USE_INTERACTIVE: Restriction
CANNOT_SPEAK_TO_NPC: Restriction
CANNOT_CHANGE_ZONE: Restriction
CANNOT_ATTACK_MONSTER: Restriction
DIALOG_BOOK: DialogType
DIALOG_DIALOG: DialogType
DIALOG_LOCKABLE: DialogType
DIALOG_PURCHASABLE: DialogType
DIALOG_GUILD_INVITATION: DialogType
DIALOG_GUILD_CREATE: DialogType
DIALOG_GUILD_RENAME: DialogType
DIALOG_MARRIAGE: DialogType
DIALOG_DUNGEON_MEETING: DialogType
DIALOG_SPELL_FORGET: DialogType
DIALOG_TELEPORTER: DialogType
DIALOG_EXCHANGE: DialogType
DIALOG_ALLIANCE_INVITATION: DialogType
DIALOG_ALLIANCE_CREATE: DialogType
DIALOG_ALLIANCE_RENAME: DialogType
DIALOG_HAVENBAG_MEETING: DialogType
NPC_SHOP: ExchangeType
PLAYER_TRADE: ExchangeType
NPC_TRADE: ExchangeType
CRAFT: ExchangeType
STORAGE: ExchangeType
SHOP_STOCK: ExchangeType
TAX_COLLECTOR: ExchangeType
NPC_MODIFY_TRADE: ExchangeType
BIDHOUSE_SELL: ExchangeType
BIDHOUSE_BUY: ExchangeType
MULTICRAFT_CRAFTER: ExchangeType
MULTICRAFT_CUSTOMER: ExchangeType
JOB_INDEX: ExchangeType
MOUNT: ExchangeType
MOUNT_STABLE: ExchangeType
NPC_RESURECT_PET: ExchangeType
NPC_TRADE_DRAGOTURKEY: ExchangeType
REALESTATE_HOUSE: ExchangeType
REALESTATE_FARM: ExchangeType
RUNES_TRADE: ExchangeType
RECYCLE_TRADE: ExchangeType
BANK: ExchangeType
TRASHBIN: ExchangeType
ALLIANCE_PRISM: ExchangeType
HAVENBAG: ExchangeType
NPC_TRADE_SEEMYOOL: ExchangeType
NPC_TRADE_RHINEETLE: ExchangeType
EVOLUTIVE_OBJECT_ELEMENTARY_RECYCLE: ExchangeType
NPC_RIDE_CAPABILITY_TRADE: ExchangeType
GUILD_CHEST: ExchangeType
FIGHT_TYPE_CHALLENGE: FightType
FIGHT_TYPE_AGGRESSION: FightType
FIGHT_TYPE_PvMA: FightType
FIGHT_TYPE_MXvM: FightType
FIGHT_TYPE_PvM: FightType
FIGHT_TYPE_PvT: FightType
FIGHT_TYPE_PvMU: FightType
FIGHT_TYPE_PVP_ARENA: FightType
FIGHT_TYPE_KOH: FightType
FIGHT_TYPE_PvPr: FightType
FIGHT_TYPE_BREACH: FightType
TEAM_TYPE_PLAYER: TeamType
TEAM_TYPE_MONSTER: TeamType
TEAM_TYPE_MUTANT: TeamType
TEAM_TYPE_TAX_COLLECTOR: TeamType
TEAM_TYPE_BAD_PLAYER: TeamType
TEAM_TYPE_PRISM: TeamType
FIGHT_OPTION_SET_SECRET: FightOption
FIGHT_OPTION_SET_TO_PARTY_ONLY: FightOption
FIGHT_OPTION_SET_CLOSED: FightOption
FIGHT_OPTION_ASK_FOR_HELP: FightOption
RESULT_LOST: FightOutcome
RESULT_DRAW: FightOutcome
RESULT_VICTORY: FightOutcome
RESULT_TAX: FightOutcome
RESULT_DEFENDER_GROUP: FightOutcome
INVISIBLE: FightInvisibilityState
DETECTED: FightInvisibilityState
VISIBLE: FightInvisibilityState
TEAM_CHALLENGER: Team
TEAM_DEFENDER: Team
TEAM_SPECTATOR: Team
TEAM_NEUTRAL: Team
GENERAL_SHORTCUT_BAR: ShortcutBar
SPELL_SHORTCUT_BAR: ShortcutBar
CHARACTER: PresetType
FORGETTABLE_SPELL: PresetType
DIRECTION_EAST: Direction
DIRECTION_SOUTH_EAST: Direction
DIRECTION_SOUTH: Direction
DIRECTION_SOUTH_WEST: Direction
DIRECTION_WEST: Direction
DIRECTION_NORTH_WEST: Direction
DIRECTION_NORTH: Direction
DIRECTION_NORTH_EAST: Direction
INVENTORY_FULL: ObjectError
CANNOT_EQUIP_TWICE: ObjectError
NOT_TRADABLE: ObjectError
CANNOT_DROP: ObjectError
CANNOT_DROP_NO_PLACE: ObjectError
CANNOT_DESTROY: ObjectError
LEVEL_TOO_LOW: ObjectError
LIVING_OBJECT_REFUSED_FOOD: ObjectError
CANNOT_UNEQUIP: ObjectError
CANNOT_EQUIP_HERE: ObjectError
CRITERIONS: ObjectError
SYMBIOTIC_OBJECT_ERROR: ObjectError
EVOLUTIVE_OBJECT_REFUSED_FOOD: ObjectError
ORIGIN_UNDEFINED: ObjectOrigin
ORIGIN_QUEST: ObjectOrigin
DISABLED: SocialRecruitmentType
AUTOMATIC: SocialRecruitmentType
MANUAL: SocialRecruitmentType
APPLICATION_ADDED: SocialApplicationState
APPLICATION_DELETED: SocialApplicationState
APPLICATION_UPDATED: SocialApplicationState
UNDEFINED: ServerType
CLASSICAL: ServerType
KOLIZEUM: ServerType
TOURNAMENT: ServerType
EPIC: ServerType
TEMPORIS: ServerType
SOCIAL_GROUP_OPERATION_OK: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_NAME_INVALID: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_ALREADY_IN_GROUP: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_NAME_ALREADY_EXISTS: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_LEAVE: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_CANCEL: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_REQUIREMENT_UNMET: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_EMBLEM_INVALID: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_TAG_INVALID: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_TAG_ALREADY_EXISTS: SocialGroupOperationResult
SOCIAL_GROUP_ERROR_UNKNOWN: SocialGroupOperationResult
SOCIAL_NOTICE_UNKNOWN_ERROR: SocialNoticeError
SOCIAL_NOTICE_INVALID_RIGHTS: SocialNoticeError
SOCIAL_NOTICE_COOLDOWN: SocialNoticeError
SOCIAL_GROUP_INVITATION_FAILED: SocialGroupInvitationState
SOCIAL_GROUP_INVITATION_SENT: SocialGroupInvitationState
SOCIAL_GROUP_INVITATION_CANCELED: SocialGroupInvitationState
SOCIAL_GROUP_INVITATION_OK: SocialGroupInvitationState
STATE_COLLECTING: TaxCollectorState
STATE_WAITING_FOR_HELP: TaxCollectorState
STATE_FIGHTING: TaxCollectorState
ENERGY: MountCharacteristic
SERENITY: MountCharacteristic
STAMINA: MountCharacteristic
LOVE: MountCharacteristic
MATURITY: MountCharacteristic
TIREDNESS: MountCharacteristic
CARRIER: MountCharacteristic
FERTILE: MountCharacteristic
PREGNANT: MountCharacteristic
ACTION_INVALID: SpellModifierActionType
ACTION_BOOST: SpellModifierActionType
ACTION_REMOVE_BOOST: SpellModifierActionType
ACTION_SET: SpellModifierActionType
INVALID_MODIFICATION: SpellModifierType
RANGE: SpellModifierType
DAMAGE: SpellModifierType
BASE_DAMAGE: SpellModifierType
HEAL_BONUS: SpellModifierType
AP_COST: SpellModifierType
CAST_INTERVAL: SpellModifierType
CRITICAL_HIT_BONUS: SpellModifierType
CAST_LINE: SpellModifierType
LOS: SpellModifierType
MAX_CAST_PER_TURN: SpellModifierType
MAX_CAST_PER_TARGET: SpellModifierType
RANGE_MAX: SpellModifierType
RANGE_MIN: SpellModifierType
OCCUPIED_CELL: SpellModifierType
FREE_CELL: SpellModifierType
VISIBLE_TARGET: SpellModifierType
PORTAL_FREE_CELL: SpellModifierType
PORTAL_PROJECTION: SpellModifierType
PRICE_ASC: RealEstateOrder
PRICE_DSC: RealEstateOrder

class AccountTag(_message.Message):
    __slots__ = ("nickname", "tag")
    NICKNAME_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    nickname: str
    tag: str
    def __init__(self, nickname: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class ActorPositionInformation(_message.Message):
    __slots__ = ("actor_id", "disposition", "actor_information")
    class ActorInformation(_message.Message):
        __slots__ = ("look", "role_play_actor", "fighter")
        class RolePlayActor(_message.Message):
            __slots__ = ("named_actor", "tax_collector_actor", "monster_group_actor", "npc_actor", "prism_actor", "portal_actor", "treasure_hunt_npc_id")
            class NamedActor(_message.Message):
                __slots__ = ("name", "humanoid_information", "mount_information")
                class Humanoid(_message.Message):
                    __slots__ = ("restrictions", "gender", "options", "account_id", "alignment_information", "mutant_information")
                    class HumanOption(_message.Message):
                        __slots__ = ("followers", "guild_information", "alliance_information", "emote_option", "title_option", "ornament_option", "object_use_option", "skill_use_option", "speed_multiplier")
                        class FollowingCharactersOption(_message.Message):
                            __slots__ = ("following_characters_looks",)
                            class IndexedEntityLook(_message.Message):
                                __slots__ = ("look", "index")
                                LOOK_FIELD_NUMBER: _ClassVar[int]
                                INDEX_FIELD_NUMBER: _ClassVar[int]
                                look: EntityLook
                                index: int
                                def __init__(self, look: _Optional[_Union[EntityLook, _Mapping]] = ..., index: _Optional[int] = ...) -> None: ...
                            FOLLOWING_CHARACTERS_LOOKS_FIELD_NUMBER: _ClassVar[int]
                            following_characters_looks: _containers.RepeatedCompositeFieldContainer[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.FollowingCharactersOption.IndexedEntityLook]
                            def __init__(self, following_characters_looks: _Optional[_Iterable[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.FollowingCharactersOption.IndexedEntityLook, _Mapping]]] = ...) -> None: ...
                        class AllianceOption(_message.Message):
                            __slots__ = ("alliance_information", "attackable_status")
                            ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                            ATTACKABLE_STATUS_FIELD_NUMBER: _ClassVar[int]
                            alliance_information: AllianceInformation
                            attackable_status: AttackableStatus
                            def __init__(self, alliance_information: _Optional[_Union[AllianceInformation, _Mapping]] = ..., attackable_status: _Optional[_Union[AttackableStatus, str]] = ...) -> None: ...
                        class EmoteOption(_message.Message):
                            __slots__ = ("emote_id", "emote_start_time")
                            EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
                            EMOTE_START_TIME_FIELD_NUMBER: _ClassVar[int]
                            emote_id: int
                            emote_start_time: str
                            def __init__(self, emote_id: _Optional[int] = ..., emote_start_time: _Optional[str] = ...) -> None: ...
                        class TitleOption(_message.Message):
                            __slots__ = ("title_id", "title_parameter")
                            TITLE_ID_FIELD_NUMBER: _ClassVar[int]
                            TITLE_PARAMETER_FIELD_NUMBER: _ClassVar[int]
                            title_id: int
                            title_parameter: str
                            def __init__(self, title_id: _Optional[int] = ..., title_parameter: _Optional[str] = ...) -> None: ...
                        class OrnamentOption(_message.Message):
                            __slots__ = ("ornament_id", "player_level", "league_id", "ladder_position")
                            ORNAMENT_ID_FIELD_NUMBER: _ClassVar[int]
                            PLAYER_LEVEL_FIELD_NUMBER: _ClassVar[int]
                            LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
                            LADDER_POSITION_FIELD_NUMBER: _ClassVar[int]
                            ornament_id: int
                            player_level: int
                            league_id: int
                            ladder_position: int
                            def __init__(self, ornament_id: _Optional[int] = ..., player_level: _Optional[int] = ..., league_id: _Optional[int] = ..., ladder_position: _Optional[int] = ...) -> None: ...
                        class ObjectUseOption(_message.Message):
                            __slots__ = ("delayed_action_type", "end_delay", "object_gid")
                            DELAYED_ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
                            END_DELAY_FIELD_NUMBER: _ClassVar[int]
                            OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
                            delayed_action_type: DelayedActionType
                            end_delay: str
                            object_gid: int
                            def __init__(self, delayed_action_type: _Optional[_Union[DelayedActionType, str]] = ..., end_delay: _Optional[str] = ..., object_gid: _Optional[int] = ...) -> None: ...
                        class SkillUseOption(_message.Message):
                            __slots__ = ("element_id", "skill_id", "skill_end_time")
                            ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
                            SKILL_ID_FIELD_NUMBER: _ClassVar[int]
                            SKILL_END_TIME_FIELD_NUMBER: _ClassVar[int]
                            element_id: int
                            skill_id: int
                            skill_end_time: str
                            def __init__(self, element_id: _Optional[int] = ..., skill_id: _Optional[int] = ..., skill_end_time: _Optional[str] = ...) -> None: ...
                        FOLLOWERS_FIELD_NUMBER: _ClassVar[int]
                        GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                        ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                        EMOTE_OPTION_FIELD_NUMBER: _ClassVar[int]
                        TITLE_OPTION_FIELD_NUMBER: _ClassVar[int]
                        ORNAMENT_OPTION_FIELD_NUMBER: _ClassVar[int]
                        OBJECT_USE_OPTION_FIELD_NUMBER: _ClassVar[int]
                        SKILL_USE_OPTION_FIELD_NUMBER: _ClassVar[int]
                        SPEED_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
                        followers: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.FollowingCharactersOption
                        guild_information: GuildInformation
                        alliance_information: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.AllianceOption
                        emote_option: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.EmoteOption
                        title_option: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.TitleOption
                        ornament_option: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.OrnamentOption
                        object_use_option: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.ObjectUseOption
                        skill_use_option: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.SkillUseOption
                        speed_multiplier: int
                        def __init__(self, followers: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.FollowingCharactersOption, _Mapping]] = ..., guild_information: _Optional[_Union[GuildInformation, _Mapping]] = ..., alliance_information: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.AllianceOption, _Mapping]] = ..., emote_option: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.EmoteOption, _Mapping]] = ..., title_option: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.TitleOption, _Mapping]] = ..., ornament_option: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.OrnamentOption, _Mapping]] = ..., object_use_option: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.ObjectUseOption, _Mapping]] = ..., skill_use_option: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption.SkillUseOption, _Mapping]] = ..., speed_multiplier: _Optional[int] = ...) -> None: ...
                    class MutantInformation(_message.Message):
                        __slots__ = ("monster_id", "power_level")
                        MONSTER_ID_FIELD_NUMBER: _ClassVar[int]
                        POWER_LEVEL_FIELD_NUMBER: _ClassVar[int]
                        monster_id: int
                        power_level: int
                        def __init__(self, monster_id: _Optional[int] = ..., power_level: _Optional[int] = ...) -> None: ...
                    RESTRICTIONS_FIELD_NUMBER: _ClassVar[int]
                    GENDER_FIELD_NUMBER: _ClassVar[int]
                    OPTIONS_FIELD_NUMBER: _ClassVar[int]
                    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
                    ALIGNMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                    MUTANT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                    restrictions: _containers.RepeatedScalarFieldContainer[Restriction]
                    gender: Gender
                    options: _containers.RepeatedCompositeFieldContainer[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption]
                    account_id: int
                    alignment_information: AlignmentInformation
                    mutant_information: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.MutantInformation
                    def __init__(self, restrictions: _Optional[_Iterable[_Union[Restriction, str]]] = ..., gender: _Optional[_Union[Gender, str]] = ..., options: _Optional[_Iterable[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.HumanOption, _Mapping]]] = ..., account_id: _Optional[int] = ..., alignment_information: _Optional[_Union[AlignmentInformation, _Mapping]] = ..., mutant_information: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid.MutantInformation, _Mapping]] = ...) -> None: ...
                class Mount(_message.Message):
                    __slots__ = ("owner_name", "level")
                    OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
                    LEVEL_FIELD_NUMBER: _ClassVar[int]
                    owner_name: str
                    level: int
                    def __init__(self, owner_name: _Optional[str] = ..., level: _Optional[int] = ...) -> None: ...
                NAME_FIELD_NUMBER: _ClassVar[int]
                HUMANOID_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                MOUNT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                name: str
                humanoid_information: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid
                mount_information: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Mount
                def __init__(self, name: _Optional[str] = ..., humanoid_information: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Humanoid, _Mapping]] = ..., mount_information: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor.Mount, _Mapping]] = ...) -> None: ...
            class TaxCollectorActor(_message.Message):
                __slots__ = ("identification", "attack")
                IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
                ATTACK_FIELD_NUMBER: _ClassVar[int]
                identification: TaxCollectorStaticInformation
                attack: int
                def __init__(self, identification: _Optional[_Union[TaxCollectorStaticInformation, _Mapping]] = ..., attack: _Optional[int] = ...) -> None: ...
            class MonsterGroupActor(_message.Message):
                __slots__ = ("identification", "loot_share", "alignment", "wave_information")
                class WaveInformation(_message.Message):
                    __slots__ = ("wave_count", "alternatives")
                    WAVE_COUNT_FIELD_NUMBER: _ClassVar[int]
                    ALTERNATIVES_FIELD_NUMBER: _ClassVar[int]
                    wave_count: int
                    alternatives: _containers.RepeatedCompositeFieldContainer[MonsterGroupStaticInformation]
                    def __init__(self, wave_count: _Optional[int] = ..., alternatives: _Optional[_Iterable[_Union[MonsterGroupStaticInformation, _Mapping]]] = ...) -> None: ...
                IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
                LOOT_SHARE_FIELD_NUMBER: _ClassVar[int]
                ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
                WAVE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                identification: MonsterGroupStaticInformation
                loot_share: int
                alignment: Alignment
                wave_information: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor.WaveInformation
                def __init__(self, identification: _Optional[_Union[MonsterGroupStaticInformation, _Mapping]] = ..., loot_share: _Optional[int] = ..., alignment: _Optional[_Union[Alignment, str]] = ..., wave_information: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor.WaveInformation, _Mapping]] = ...) -> None: ...
            class NpcStaticInformation(_message.Message):
                __slots__ = ("npc_id", "gender", "special_artwork_id", "quests")
                class Quests(_message.Message):
                    __slots__ = ("quests_to_valid", "quests_to_start")
                    QUESTS_TO_VALID_FIELD_NUMBER: _ClassVar[int]
                    QUESTS_TO_START_FIELD_NUMBER: _ClassVar[int]
                    quests_to_valid: _containers.RepeatedScalarFieldContainer[int]
                    quests_to_start: _containers.RepeatedScalarFieldContainer[int]
                    def __init__(self, quests_to_valid: _Optional[_Iterable[int]] = ..., quests_to_start: _Optional[_Iterable[int]] = ...) -> None: ...
                NPC_ID_FIELD_NUMBER: _ClassVar[int]
                GENDER_FIELD_NUMBER: _ClassVar[int]
                SPECIAL_ARTWORK_ID_FIELD_NUMBER: _ClassVar[int]
                QUESTS_FIELD_NUMBER: _ClassVar[int]
                npc_id: int
                gender: Gender
                special_artwork_id: int
                quests: ActorPositionInformation.ActorInformation.RolePlayActor.NpcStaticInformation.Quests
                def __init__(self, npc_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ..., special_artwork_id: _Optional[int] = ..., quests: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NpcStaticInformation.Quests, _Mapping]] = ...) -> None: ...
            NAMED_ACTOR_FIELD_NUMBER: _ClassVar[int]
            TAX_COLLECTOR_ACTOR_FIELD_NUMBER: _ClassVar[int]
            MONSTER_GROUP_ACTOR_FIELD_NUMBER: _ClassVar[int]
            NPC_ACTOR_FIELD_NUMBER: _ClassVar[int]
            PRISM_ACTOR_FIELD_NUMBER: _ClassVar[int]
            PORTAL_ACTOR_FIELD_NUMBER: _ClassVar[int]
            TREASURE_HUNT_NPC_ID_FIELD_NUMBER: _ClassVar[int]
            named_actor: ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor
            tax_collector_actor: ActorPositionInformation.ActorInformation.RolePlayActor.TaxCollectorActor
            monster_group_actor: ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor
            npc_actor: ActorPositionInformation.ActorInformation.RolePlayActor.NpcStaticInformation
            prism_actor: PrismInformation
            portal_actor: PortalInformation
            treasure_hunt_npc_id: int
            def __init__(self, named_actor: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NamedActor, _Mapping]] = ..., tax_collector_actor: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.TaxCollectorActor, _Mapping]] = ..., monster_group_actor: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.MonsterGroupActor, _Mapping]] = ..., npc_actor: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor.NpcStaticInformation, _Mapping]] = ..., prism_actor: _Optional[_Union[PrismInformation, _Mapping]] = ..., portal_actor: _Optional[_Union[PortalInformation, _Mapping]] = ..., treasure_hunt_npc_id: _Optional[int] = ...) -> None: ...
        class FightFighterInformation(_message.Message):
            __slots__ = ("spawn_information", "wave", "stats", "previous_positions", "named_fighter", "ai_fighter", "entity_fighter")
            class NamedFighterInformation(_message.Message):
                __slots__ = ("name", "status", "league_id", "ladder_position", "hidden_in_pre_fight", "character_information", "mutant_information")
                class FightCharacterInformation(_message.Message):
                    __slots__ = ("level", "alignment_information", "breed_id", "gender")
                    LEVEL_FIELD_NUMBER: _ClassVar[int]
                    ALIGNMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                    BREED_ID_FIELD_NUMBER: _ClassVar[int]
                    GENDER_FIELD_NUMBER: _ClassVar[int]
                    level: int
                    alignment_information: AlignmentInformation
                    breed_id: int
                    gender: Gender
                    def __init__(self, level: _Optional[int] = ..., alignment_information: _Optional[_Union[AlignmentInformation, _Mapping]] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ...) -> None: ...
                class FightMutantInformation(_message.Message):
                    __slots__ = ("power_level",)
                    POWER_LEVEL_FIELD_NUMBER: _ClassVar[int]
                    power_level: int
                    def __init__(self, power_level: _Optional[int] = ...) -> None: ...
                NAME_FIELD_NUMBER: _ClassVar[int]
                STATUS_FIELD_NUMBER: _ClassVar[int]
                LEAGUE_ID_FIELD_NUMBER: _ClassVar[int]
                LADDER_POSITION_FIELD_NUMBER: _ClassVar[int]
                HIDDEN_IN_PRE_FIGHT_FIELD_NUMBER: _ClassVar[int]
                CHARACTER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                MUTANT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                name: str
                status: CharacterStatus
                league_id: int
                ladder_position: int
                hidden_in_pre_fight: bool
                character_information: ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation.FightCharacterInformation
                mutant_information: ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation.FightMutantInformation
                def __init__(self, name: _Optional[str] = ..., status: _Optional[_Union[CharacterStatus, _Mapping]] = ..., league_id: _Optional[int] = ..., ladder_position: _Optional[int] = ..., hidden_in_pre_fight: bool = ..., character_information: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation.FightCharacterInformation, _Mapping]] = ..., mutant_information: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation.FightMutantInformation, _Mapping]] = ...) -> None: ...
            class AIFighterInformation(_message.Message):
                __slots__ = ("monster_fighter_information", "tax_collector_information")
                class MonsterFighter(_message.Message):
                    __slots__ = ("monster_gid", "creature_grade", "creature_level", "alignment_information")
                    MONSTER_GID_FIELD_NUMBER: _ClassVar[int]
                    CREATURE_GRADE_FIELD_NUMBER: _ClassVar[int]
                    CREATURE_LEVEL_FIELD_NUMBER: _ClassVar[int]
                    ALIGNMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                    monster_gid: int
                    creature_grade: int
                    creature_level: int
                    alignment_information: AlignmentInformation
                    def __init__(self, monster_gid: _Optional[int] = ..., creature_grade: _Optional[int] = ..., creature_level: _Optional[int] = ..., alignment_information: _Optional[_Union[AlignmentInformation, _Mapping]] = ...) -> None: ...
                class TaxCollectorFighter(_message.Message):
                    __slots__ = ("first_name_id", "last_name_id")
                    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
                    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
                    first_name_id: int
                    last_name_id: int
                    def __init__(self, first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ...) -> None: ...
                MONSTER_FIGHTER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                TAX_COLLECTOR_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                monster_fighter_information: ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation.MonsterFighter
                tax_collector_information: ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation.TaxCollectorFighter
                def __init__(self, monster_fighter_information: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation.MonsterFighter, _Mapping]] = ..., tax_collector_information: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation.TaxCollectorFighter, _Mapping]] = ...) -> None: ...
            class EntityFighterInformation(_message.Message):
                __slots__ = ("entity_model_id", "level", "master_id")
                ENTITY_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
                LEVEL_FIELD_NUMBER: _ClassVar[int]
                MASTER_ID_FIELD_NUMBER: _ClassVar[int]
                entity_model_id: int
                level: int
                master_id: int
                def __init__(self, entity_model_id: _Optional[int] = ..., level: _Optional[int] = ..., master_id: _Optional[int] = ...) -> None: ...
            SPAWN_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            WAVE_FIELD_NUMBER: _ClassVar[int]
            STATS_FIELD_NUMBER: _ClassVar[int]
            PREVIOUS_POSITIONS_FIELD_NUMBER: _ClassVar[int]
            NAMED_FIGHTER_FIELD_NUMBER: _ClassVar[int]
            AI_FIGHTER_FIELD_NUMBER: _ClassVar[int]
            ENTITY_FIGHTER_FIELD_NUMBER: _ClassVar[int]
            spawn_information: SpawnInformation
            wave: int
            stats: FightCharacteristics
            previous_positions: _containers.RepeatedScalarFieldContainer[int]
            named_fighter: ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation
            ai_fighter: ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation
            entity_fighter: ActorPositionInformation.ActorInformation.FightFighterInformation.EntityFighterInformation
            def __init__(self, spawn_information: _Optional[_Union[SpawnInformation, _Mapping]] = ..., wave: _Optional[int] = ..., stats: _Optional[_Union[FightCharacteristics, _Mapping]] = ..., previous_positions: _Optional[_Iterable[int]] = ..., named_fighter: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.NamedFighterInformation, _Mapping]] = ..., ai_fighter: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.AIFighterInformation, _Mapping]] = ..., entity_fighter: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation.EntityFighterInformation, _Mapping]] = ...) -> None: ...
        LOOK_FIELD_NUMBER: _ClassVar[int]
        ROLE_PLAY_ACTOR_FIELD_NUMBER: _ClassVar[int]
        FIGHTER_FIELD_NUMBER: _ClassVar[int]
        look: EntityLook
        role_play_actor: ActorPositionInformation.ActorInformation.RolePlayActor
        fighter: ActorPositionInformation.ActorInformation.FightFighterInformation
        def __init__(self, look: _Optional[_Union[EntityLook, _Mapping]] = ..., role_play_actor: _Optional[_Union[ActorPositionInformation.ActorInformation.RolePlayActor, _Mapping]] = ..., fighter: _Optional[_Union[ActorPositionInformation.ActorInformation.FightFighterInformation, _Mapping]] = ...) -> None: ...
    ACTOR_ID_FIELD_NUMBER: _ClassVar[int]
    DISPOSITION_FIELD_NUMBER: _ClassVar[int]
    ACTOR_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    actor_id: int
    disposition: EntityDisposition
    actor_information: ActorPositionInformation.ActorInformation
    def __init__(self, actor_id: _Optional[int] = ..., disposition: _Optional[_Union[EntityDisposition, _Mapping]] = ..., actor_information: _Optional[_Union[ActorPositionInformation.ActorInformation, _Mapping]] = ...) -> None: ...

class SpawnInformation(_message.Message):
    __slots__ = ("team", "alive", "position")
    TEAM_FIELD_NUMBER: _ClassVar[int]
    ALIVE_FIELD_NUMBER: _ClassVar[int]
    POSITION_FIELD_NUMBER: _ClassVar[int]
    team: Team
    alive: bool
    position: ActorPositionInformation
    def __init__(self, team: _Optional[_Union[Team, str]] = ..., alive: bool = ..., position: _Optional[_Union[ActorPositionInformation, _Mapping]] = ...) -> None: ...

class AllianceInformation(_message.Message):
    __slots__ = ("uid", "tag", "name", "emblem", "card_information")
    class AllianceCardInformation(_message.Message):
        __slots__ = ("creation_date", "members_number", "subarea_number", "tax_collector_number", "recruitment")
        CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
        MEMBERS_NUMBER_FIELD_NUMBER: _ClassVar[int]
        SUBAREA_NUMBER_FIELD_NUMBER: _ClassVar[int]
        TAX_COLLECTOR_NUMBER_FIELD_NUMBER: _ClassVar[int]
        RECRUITMENT_FIELD_NUMBER: _ClassVar[int]
        creation_date: int
        members_number: int
        subarea_number: int
        tax_collector_number: int
        recruitment: AllianceRecruitmentInformation
        def __init__(self, creation_date: _Optional[int] = ..., members_number: _Optional[int] = ..., subarea_number: _Optional[int] = ..., tax_collector_number: _Optional[int] = ..., recruitment: _Optional[_Union[AllianceRecruitmentInformation, _Mapping]] = ...) -> None: ...
    UID_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    EMBLEM_FIELD_NUMBER: _ClassVar[int]
    CARD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    uid: str
    tag: str
    name: str
    emblem: SocialEmblem
    card_information: AllianceInformation.AllianceCardInformation
    def __init__(self, uid: _Optional[str] = ..., tag: _Optional[str] = ..., name: _Optional[str] = ..., emblem: _Optional[_Union[SocialEmblem, _Mapping]] = ..., card_information: _Optional[_Union[AllianceInformation.AllianceCardInformation, _Mapping]] = ...) -> None: ...

class BreachBranch(_message.Message):
    __slots__ = ("room", "element", "bosses", "map_id", "score", "relative_score", "monsters", "extended_information")
    class ExtendedBreachBranch(_message.Message):
        __slots__ = ("rewards", "modifier", "price", "unlock_price")
        REWARDS_FIELD_NUMBER: _ClassVar[int]
        MODIFIER_FIELD_NUMBER: _ClassVar[int]
        PRICE_FIELD_NUMBER: _ClassVar[int]
        UNLOCK_PRICE_FIELD_NUMBER: _ClassVar[int]
        rewards: _containers.RepeatedCompositeFieldContainer[BreachReward]
        modifier: int
        price: int
        unlock_price: int
        def __init__(self, rewards: _Optional[_Iterable[_Union[BreachReward, _Mapping]]] = ..., modifier: _Optional[int] = ..., price: _Optional[int] = ..., unlock_price: _Optional[int] = ...) -> None: ...
    ROOM_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_FIELD_NUMBER: _ClassVar[int]
    BOSSES_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    SCORE_FIELD_NUMBER: _ClassVar[int]
    RELATIVE_SCORE_FIELD_NUMBER: _ClassVar[int]
    MONSTERS_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    room: int
    element: int
    bosses: _containers.RepeatedCompositeFieldContainer[MonsterInGroupInformation]
    map_id: int
    score: int
    relative_score: int
    monsters: _containers.RepeatedCompositeFieldContainer[MonsterInGroupInformation]
    extended_information: BreachBranch.ExtendedBreachBranch
    def __init__(self, room: _Optional[int] = ..., element: _Optional[int] = ..., bosses: _Optional[_Iterable[_Union[MonsterInGroupInformation, _Mapping]]] = ..., map_id: _Optional[int] = ..., score: _Optional[int] = ..., relative_score: _Optional[int] = ..., monsters: _Optional[_Iterable[_Union[MonsterInGroupInformation, _Mapping]]] = ..., extended_information: _Optional[_Union[BreachBranch.ExtendedBreachBranch, _Mapping]] = ...) -> None: ...

class BreachReward(_message.Message):
    __slots__ = ("id", "buy_locks", "buy_criterion", "remaining_quantity", "price")
    class BreachRewardLock(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        BREACH_REWARD_LOCK_OWNER: _ClassVar[BreachReward.BreachRewardLock]
        BREACH_REWARD_LOCK_FIGHTER: _ClassVar[BreachReward.BreachRewardLock]
        BREACH_REWARD_LOCK_RESOURCES: _ClassVar[BreachReward.BreachRewardLock]
        BREACH_REWARD_LOCK_CRITERION: _ClassVar[BreachReward.BreachRewardLock]
        BREACH_REWARD_LOCK_USELESS: _ClassVar[BreachReward.BreachRewardLock]
        BREACH_REWARD_MAX_PURCHASE_REACHED: _ClassVar[BreachReward.BreachRewardLock]
    BREACH_REWARD_LOCK_OWNER: BreachReward.BreachRewardLock
    BREACH_REWARD_LOCK_FIGHTER: BreachReward.BreachRewardLock
    BREACH_REWARD_LOCK_RESOURCES: BreachReward.BreachRewardLock
    BREACH_REWARD_LOCK_CRITERION: BreachReward.BreachRewardLock
    BREACH_REWARD_LOCK_USELESS: BreachReward.BreachRewardLock
    BREACH_REWARD_MAX_PURCHASE_REACHED: BreachReward.BreachRewardLock
    ID_FIELD_NUMBER: _ClassVar[int]
    BUY_LOCKS_FIELD_NUMBER: _ClassVar[int]
    BUY_CRITERION_FIELD_NUMBER: _ClassVar[int]
    REMAINING_QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    id: int
    buy_locks: _containers.RepeatedScalarFieldContainer[BreachReward.BreachRewardLock]
    buy_criterion: str
    remaining_quantity: int
    price: int
    def __init__(self, id: _Optional[int] = ..., buy_locks: _Optional[_Iterable[_Union[BreachReward.BreachRewardLock, str]]] = ..., buy_criterion: _Optional[str] = ..., remaining_quantity: _Optional[int] = ..., price: _Optional[int] = ...) -> None: ...

class Challenge(_message.Message):
    __slots__ = ("challenge_id", "targets", "drop_bonus", "xp_bonus", "state")
    class ChallengeState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        CHALLENGE_COMPLETED: _ClassVar[Challenge.ChallengeState]
        CHALLENGE_FAILED: _ClassVar[Challenge.ChallengeState]
        CHALLENGE_RUNNING: _ClassVar[Challenge.ChallengeState]
    CHALLENGE_COMPLETED: Challenge.ChallengeState
    CHALLENGE_FAILED: Challenge.ChallengeState
    CHALLENGE_RUNNING: Challenge.ChallengeState
    CHALLENGE_ID_FIELD_NUMBER: _ClassVar[int]
    TARGETS_FIELD_NUMBER: _ClassVar[int]
    DROP_BONUS_FIELD_NUMBER: _ClassVar[int]
    XP_BONUS_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    challenge_id: int
    targets: _containers.RepeatedCompositeFieldContainer[ChallengeTarget]
    drop_bonus: int
    xp_bonus: int
    state: Challenge.ChallengeState
    def __init__(self, challenge_id: _Optional[int] = ..., targets: _Optional[_Iterable[_Union[ChallengeTarget, _Mapping]]] = ..., drop_bonus: _Optional[int] = ..., xp_bonus: _Optional[int] = ..., state: _Optional[_Union[Challenge.ChallengeState, str]] = ...) -> None: ...

class ChallengeTarget(_message.Message):
    __slots__ = ("target_id", "target_cell", "attackers_id")
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_CELL_FIELD_NUMBER: _ClassVar[int]
    ATTACKERS_ID_FIELD_NUMBER: _ClassVar[int]
    target_id: int
    target_cell: int
    attackers_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, target_id: _Optional[int] = ..., target_cell: _Optional[int] = ..., attackers_id: _Optional[_Iterable[int]] = ...) -> None: ...

class Character(_message.Message):
    __slots__ = ("id", "character_basic_information", "character_remodeling_information")
    class CharacterBasicInformation(_message.Message):
        __slots__ = ("name", "level", "character_look", "rank", "social_member")
        class SocialMember(_message.Message):
            __slots__ = ("breed_id", "gender", "state", "hours_since_last_connection", "account_id", "status", "rank_id", "enrollment_date", "ava_role_id", "guild_member")
            class GuildMember(_message.Message):
                __slots__ = ("given_experience", "experience_given_percent", "alignment", "mood_smiley_id", "achievement_points", "haven_bag_shared", "note")
                class PlayerNote(_message.Message):
                    __slots__ = ("content", "last_edit_date")
                    CONTENT_FIELD_NUMBER: _ClassVar[int]
                    LAST_EDIT_DATE_FIELD_NUMBER: _ClassVar[int]
                    content: str
                    last_edit_date: int
                    def __init__(self, content: _Optional[str] = ..., last_edit_date: _Optional[int] = ...) -> None: ...
                GIVEN_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
                EXPERIENCE_GIVEN_PERCENT_FIELD_NUMBER: _ClassVar[int]
                ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
                MOOD_SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
                ACHIEVEMENT_POINTS_FIELD_NUMBER: _ClassVar[int]
                HAVEN_BAG_SHARED_FIELD_NUMBER: _ClassVar[int]
                NOTE_FIELD_NUMBER: _ClassVar[int]
                given_experience: int
                experience_given_percent: int
                alignment: Alignment
                mood_smiley_id: int
                achievement_points: int
                haven_bag_shared: bool
                note: Character.CharacterBasicInformation.SocialMember.GuildMember.PlayerNote
                def __init__(self, given_experience: _Optional[int] = ..., experience_given_percent: _Optional[int] = ..., alignment: _Optional[_Union[Alignment, str]] = ..., mood_smiley_id: _Optional[int] = ..., achievement_points: _Optional[int] = ..., haven_bag_shared: bool = ..., note: _Optional[_Union[Character.CharacterBasicInformation.SocialMember.GuildMember.PlayerNote, _Mapping]] = ...) -> None: ...
            BREED_ID_FIELD_NUMBER: _ClassVar[int]
            GENDER_FIELD_NUMBER: _ClassVar[int]
            STATE_FIELD_NUMBER: _ClassVar[int]
            HOURS_SINCE_LAST_CONNECTION_FIELD_NUMBER: _ClassVar[int]
            ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
            STATUS_FIELD_NUMBER: _ClassVar[int]
            RANK_ID_FIELD_NUMBER: _ClassVar[int]
            ENROLLMENT_DATE_FIELD_NUMBER: _ClassVar[int]
            AVA_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
            GUILD_MEMBER_FIELD_NUMBER: _ClassVar[int]
            breed_id: int
            gender: Gender
            state: CharacterState
            hours_since_last_connection: int
            account_id: int
            status: CharacterStatus
            rank_id: int
            enrollment_date: int
            ava_role_id: int
            guild_member: Character.CharacterBasicInformation.SocialMember.GuildMember
            def __init__(self, breed_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ..., state: _Optional[_Union[CharacterState, str]] = ..., hours_since_last_connection: _Optional[int] = ..., account_id: _Optional[int] = ..., status: _Optional[_Union[CharacterStatus, _Mapping]] = ..., rank_id: _Optional[int] = ..., enrollment_date: _Optional[int] = ..., ava_role_id: _Optional[int] = ..., guild_member: _Optional[_Union[Character.CharacterBasicInformation.SocialMember.GuildMember, _Mapping]] = ...) -> None: ...
        class CharacterLook(_message.Message):
            __slots__ = ("look", "breed_id", "guild_information", "alliance_information", "grade", "base_information")
            class CharacterBaseInformation(_message.Message):
                __slots__ = ("gender", "epic_information", "party_member_information", "party_invitation_member_information")
                class CharacterEpicInformation(_message.Message):
                    __slots__ = ("death_state", "death_count", "death_max_level")
                    class EpicDeathState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
                        __slots__ = ()
                        DEATH_STATE_ALIVE: _ClassVar[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState]
                        DEATH_STATE_DEAD: _ClassVar[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState]
                        DEATH_STATE_WAITING_CONFIRMATION: _ClassVar[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState]
                    DEATH_STATE_ALIVE: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState
                    DEATH_STATE_DEAD: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState
                    DEATH_STATE_WAITING_CONFIRMATION: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState
                    DEATH_STATE_FIELD_NUMBER: _ClassVar[int]
                    DEATH_COUNT_FIELD_NUMBER: _ClassVar[int]
                    DEATH_MAX_LEVEL_FIELD_NUMBER: _ClassVar[int]
                    death_state: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState
                    death_count: int
                    death_max_level: int
                    def __init__(self, death_state: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation.EpicDeathState, str]] = ..., death_count: _Optional[int] = ..., death_max_level: _Optional[int] = ...) -> None: ...
                class PartyMemberInformation(_message.Message):
                    __slots__ = ("commons_information", "initiative", "alignment", "coordinates", "status", "entities", "rank")
                    COMMONS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                    INITIATIVE_FIELD_NUMBER: _ClassVar[int]
                    ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
                    COORDINATES_FIELD_NUMBER: _ClassVar[int]
                    STATUS_FIELD_NUMBER: _ClassVar[int]
                    ENTITIES_FIELD_NUMBER: _ClassVar[int]
                    RANK_FIELD_NUMBER: _ClassVar[int]
                    commons_information: PartyUpdateCommonsInformation
                    initiative: int
                    alignment: Alignment
                    coordinates: MapExtendedCoordinates
                    status: CharacterStatus
                    entities: _containers.RepeatedCompositeFieldContainer[PartyEntity]
                    rank: int
                    def __init__(self, commons_information: _Optional[_Union[PartyUpdateCommonsInformation, _Mapping]] = ..., initiative: _Optional[int] = ..., alignment: _Optional[_Union[Alignment, str]] = ..., coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ..., status: _Optional[_Union[CharacterStatus, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[PartyEntity, _Mapping]]] = ..., rank: _Optional[int] = ...) -> None: ...
                class PartyInvitationMemberInformation(_message.Message):
                    __slots__ = ("coordinates", "entities")
                    COORDINATES_FIELD_NUMBER: _ClassVar[int]
                    ENTITIES_FIELD_NUMBER: _ClassVar[int]
                    coordinates: MapExtendedCoordinates
                    entities: _containers.RepeatedCompositeFieldContainer[PartyEntity]
                    def __init__(self, coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ..., entities: _Optional[_Iterable[_Union[PartyEntity, _Mapping]]] = ...) -> None: ...
                GENDER_FIELD_NUMBER: _ClassVar[int]
                EPIC_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                PARTY_MEMBER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                PARTY_INVITATION_MEMBER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                gender: Gender
                epic_information: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation
                party_member_information: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.PartyMemberInformation
                party_invitation_member_information: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.PartyInvitationMemberInformation
                def __init__(self, gender: _Optional[_Union[Gender, str]] = ..., epic_information: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.CharacterEpicInformation, _Mapping]] = ..., party_member_information: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.PartyMemberInformation, _Mapping]] = ..., party_invitation_member_information: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation.PartyInvitationMemberInformation, _Mapping]] = ...) -> None: ...
            LOOK_FIELD_NUMBER: _ClassVar[int]
            BREED_ID_FIELD_NUMBER: _ClassVar[int]
            GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            GRADE_FIELD_NUMBER: _ClassVar[int]
            BASE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            look: EntityLook
            breed_id: int
            guild_information: GuildInformation
            alliance_information: AllianceInformation
            grade: int
            base_information: Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation
            def __init__(self, look: _Optional[_Union[EntityLook, _Mapping]] = ..., breed_id: _Optional[int] = ..., guild_information: _Optional[_Union[GuildInformation, _Mapping]] = ..., alliance_information: _Optional[_Union[AllianceInformation, _Mapping]] = ..., grade: _Optional[int] = ..., base_information: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook.CharacterBaseInformation, _Mapping]] = ...) -> None: ...
        NAME_FIELD_NUMBER: _ClassVar[int]
        LEVEL_FIELD_NUMBER: _ClassVar[int]
        CHARACTER_LOOK_FIELD_NUMBER: _ClassVar[int]
        RANK_FIELD_NUMBER: _ClassVar[int]
        SOCIAL_MEMBER_FIELD_NUMBER: _ClassVar[int]
        name: str
        level: int
        character_look: Character.CharacterBasicInformation.CharacterLook
        rank: RankInformation
        social_member: Character.CharacterBasicInformation.SocialMember
        def __init__(self, name: _Optional[str] = ..., level: _Optional[int] = ..., character_look: _Optional[_Union[Character.CharacterBasicInformation.CharacterLook, _Mapping]] = ..., rank: _Optional[_Union[RankInformation, _Mapping]] = ..., social_member: _Optional[_Union[Character.CharacterBasicInformation.SocialMember, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_BASIC_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_REMODELING_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    character_basic_information: Character.CharacterBasicInformation
    character_remodeling_information: CharacterRemodelingInformation
    def __init__(self, id: _Optional[int] = ..., character_basic_information: _Optional[_Union[Character.CharacterBasicInformation, _Mapping]] = ..., character_remodeling_information: _Optional[_Union[CharacterRemodelingInformation, _Mapping]] = ...) -> None: ...

class CharacterRemodelingInformation(_message.Message):
    __slots__ = ("name", "breed_id", "gender", "colors", "cosmeticId", "character_to_remodel_information")
    class CharacterToRemodelInformation(_message.Message):
        __slots__ = ("possible_change_mask", "mandatory_change_mask")
        POSSIBLE_CHANGE_MASK_FIELD_NUMBER: _ClassVar[int]
        MANDATORY_CHANGE_MASK_FIELD_NUMBER: _ClassVar[int]
        possible_change_mask: int
        mandatory_change_mask: int
        def __init__(self, possible_change_mask: _Optional[int] = ..., mandatory_change_mask: _Optional[int] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    COLORS_FIELD_NUMBER: _ClassVar[int]
    COSMETICID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_TO_REMODEL_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    name: str
    breed_id: int
    gender: Gender
    colors: _containers.RepeatedScalarFieldContainer[int]
    cosmeticId: int
    character_to_remodel_information: CharacterRemodelingInformation.CharacterToRemodelInformation
    def __init__(self, name: _Optional[str] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ..., colors: _Optional[_Iterable[int]] = ..., cosmeticId: _Optional[int] = ..., character_to_remodel_information: _Optional[_Union[CharacterRemodelingInformation.CharacterToRemodelInformation, _Mapping]] = ...) -> None: ...

class PartyEntity(_message.Message):
    __slots__ = ("index_id", "entity_model_id", "look", "entity_member")
    class EntityMember(_message.Message):
        __slots__ = ("initiative", "commons_information")
        INITIATIVE_FIELD_NUMBER: _ClassVar[int]
        COMMONS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        initiative: int
        commons_information: PartyUpdateCommonsInformation
        def __init__(self, initiative: _Optional[int] = ..., commons_information: _Optional[_Union[PartyUpdateCommonsInformation, _Mapping]] = ...) -> None: ...
    INDEX_ID_FIELD_NUMBER: _ClassVar[int]
    ENTITY_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    ENTITY_MEMBER_FIELD_NUMBER: _ClassVar[int]
    index_id: int
    entity_model_id: int
    look: EntityLook
    entity_member: PartyEntity.EntityMember
    def __init__(self, index_id: _Optional[int] = ..., entity_model_id: _Optional[int] = ..., look: _Optional[_Union[EntityLook, _Mapping]] = ..., entity_member: _Optional[_Union[PartyEntity.EntityMember, _Mapping]] = ...) -> None: ...

class PartyUpdateCommonsInformation(_message.Message):
    __slots__ = ("life_point", "max_life_points", "prospecting", "regen_rate")
    LIFE_POINT_FIELD_NUMBER: _ClassVar[int]
    MAX_LIFE_POINTS_FIELD_NUMBER: _ClassVar[int]
    PROSPECTING_FIELD_NUMBER: _ClassVar[int]
    REGEN_RATE_FIELD_NUMBER: _ClassVar[int]
    life_point: int
    max_life_points: int
    prospecting: int
    regen_rate: int
    def __init__(self, life_point: _Optional[int] = ..., max_life_points: _Optional[int] = ..., prospecting: _Optional[int] = ..., regen_rate: _Optional[int] = ...) -> None: ...

class CharacterCharacteristic(_message.Message):
    __slots__ = ("characteristic_id", "value", "detailed", "usable")
    CHARACTERISTIC_ID_FIELD_NUMBER: _ClassVar[int]
    VALUE_FIELD_NUMBER: _ClassVar[int]
    DETAILED_FIELD_NUMBER: _ClassVar[int]
    USABLE_FIELD_NUMBER: _ClassVar[int]
    characteristic_id: int
    value: CharacterCharacteristicValue
    detailed: CharacterCharacteristicDetailed
    usable: CharacterCharacteristicDetailedUsable
    def __init__(self, characteristic_id: _Optional[int] = ..., value: _Optional[_Union[CharacterCharacteristicValue, _Mapping]] = ..., detailed: _Optional[_Union[CharacterCharacteristicDetailed, _Mapping]] = ..., usable: _Optional[_Union[CharacterCharacteristicDetailedUsable, _Mapping]] = ...) -> None: ...

class CharacterCharacteristicValue(_message.Message):
    __slots__ = ("total",)
    TOTAL_FIELD_NUMBER: _ClassVar[int]
    total: int
    def __init__(self, total: _Optional[int] = ...) -> None: ...

class CharacterCharacteristicDetailed(_message.Message):
    __slots__ = ("base", "additional", "objects_and_mount_bonus", "alignment_gift_bonus", "context_modification", "temporary")
    BASE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_AND_MOUNT_BONUS_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_GIFT_BONUS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_FIELD_NUMBER: _ClassVar[int]
    base: int
    additional: int
    objects_and_mount_bonus: int
    alignment_gift_bonus: int
    context_modification: int
    temporary: int
    def __init__(self, base: _Optional[int] = ..., additional: _Optional[int] = ..., objects_and_mount_bonus: _Optional[int] = ..., alignment_gift_bonus: _Optional[int] = ..., context_modification: _Optional[int] = ..., temporary: _Optional[int] = ...) -> None: ...

class CharacterCharacteristicDetailedUsable(_message.Message):
    __slots__ = ("base", "additional", "objects_and_mount_bonus", "alignment_gift_bonus", "context_modification", "used", "temporary")
    BASE_FIELD_NUMBER: _ClassVar[int]
    ADDITIONAL_FIELD_NUMBER: _ClassVar[int]
    OBJECTS_AND_MOUNT_BONUS_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_GIFT_BONUS_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_MODIFICATION_FIELD_NUMBER: _ClassVar[int]
    USED_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_FIELD_NUMBER: _ClassVar[int]
    base: int
    additional: int
    objects_and_mount_bonus: int
    alignment_gift_bonus: int
    context_modification: int
    used: int
    temporary: int
    def __init__(self, base: _Optional[int] = ..., additional: _Optional[int] = ..., objects_and_mount_bonus: _Optional[int] = ..., alignment_gift_bonus: _Optional[int] = ..., context_modification: _Optional[int] = ..., used: _Optional[int] = ..., temporary: _Optional[int] = ...) -> None: ...

class CharacterInformation(_message.Message):
    __slots__ = ("character_id", "name", "breed_id", "gender", "level", "account_id", "account_tag", "account_nickname", "status")
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_NICKNAME_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    character_id: int
    name: str
    breed_id: int
    gender: Gender
    level: int
    account_id: int
    account_tag: str
    account_nickname: str
    status: CharacterStatus
    def __init__(self, character_id: _Optional[int] = ..., name: _Optional[str] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ..., level: _Optional[int] = ..., account_id: _Optional[int] = ..., account_tag: _Optional[str] = ..., account_nickname: _Optional[str] = ..., status: _Optional[_Union[CharacterStatus, _Mapping]] = ...) -> None: ...

class CharacterStatus(_message.Message):
    __slots__ = ("status", "message")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STATUS_OFFLINE: _ClassVar[CharacterStatus.Status]
        STATUS_AVAILABLE: _ClassVar[CharacterStatus.Status]
        STATUS_IDLE: _ClassVar[CharacterStatus.Status]
        STATUS_AFK: _ClassVar[CharacterStatus.Status]
        STATUS_PRIVATE: _ClassVar[CharacterStatus.Status]
        STATUS_SOLO: _ClassVar[CharacterStatus.Status]
        STATUS_UNKNOWN: _ClassVar[CharacterStatus.Status]
    STATUS_OFFLINE: CharacterStatus.Status
    STATUS_AVAILABLE: CharacterStatus.Status
    STATUS_IDLE: CharacterStatus.Status
    STATUS_AFK: CharacterStatus.Status
    STATUS_PRIVATE: CharacterStatus.Status
    STATUS_SOLO: CharacterStatus.Status
    STATUS_UNKNOWN: CharacterStatus.Status
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    status: CharacterStatus.Status
    message: str
    def __init__(self, status: _Optional[_Union[CharacterStatus.Status, str]] = ..., message: _Optional[str] = ...) -> None: ...

class PlayerSearch(_message.Message):
    __slots__ = ("search_by_character_name", "search_by_account")
    class SearchByCharacterName(_message.Message):
        __slots__ = ("name",)
        NAME_FIELD_NUMBER: _ClassVar[int]
        name: str
        def __init__(self, name: _Optional[str] = ...) -> None: ...
    class SearchByAccount(_message.Message):
        __slots__ = ("name", "tag")
        NAME_FIELD_NUMBER: _ClassVar[int]
        TAG_FIELD_NUMBER: _ClassVar[int]
        name: str
        tag: str
        def __init__(self, name: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...
    SEARCH_BY_CHARACTER_NAME_FIELD_NUMBER: _ClassVar[int]
    SEARCH_BY_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    search_by_character_name: PlayerSearch.SearchByCharacterName
    search_by_account: PlayerSearch.SearchByAccount
    def __init__(self, search_by_character_name: _Optional[_Union[PlayerSearch.SearchByCharacterName, _Mapping]] = ..., search_by_account: _Optional[_Union[PlayerSearch.SearchByAccount, _Mapping]] = ...) -> None: ...

class AllianceMemberInformation(_message.Message):
    __slots__ = ("information", "ava_role_id")
    INFORMATION_FIELD_NUMBER: _ClassVar[int]
    AVA_ROLE_ID_FIELD_NUMBER: _ClassVar[int]
    information: Character
    ava_role_id: int
    def __init__(self, information: _Optional[_Union[Character, _Mapping]] = ..., ava_role_id: _Optional[int] = ...) -> None: ...

class SocialApplicationInformation(_message.Message):
    __slots__ = ("player_information", "apply_text", "creation_date")
    PLAYER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    APPLY_TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATION_DATE_FIELD_NUMBER: _ClassVar[int]
    player_information: CharacterInformation
    apply_text: str
    creation_date: int
    def __init__(self, player_information: _Optional[_Union[CharacterInformation, _Mapping]] = ..., apply_text: _Optional[str] = ..., creation_date: _Optional[int] = ...) -> None: ...

class CharacterCharacteristics(_message.Message):
    __slots__ = ("experience", "experience_level_floor", "experience_next_level_floor", "experience_bonus_limit", "kamas", "alignment_information", "critical_hit_weapon", "characteristics", "spell_modifiers", "probation_time")
    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_NEXT_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_BONUS_LIMIT_FIELD_NUMBER: _ClassVar[int]
    KAMAS_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    CRITICAL_HIT_WEAPON_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    SPELL_MODIFIERS_FIELD_NUMBER: _ClassVar[int]
    PROBATION_TIME_FIELD_NUMBER: _ClassVar[int]
    experience: int
    experience_level_floor: int
    experience_next_level_floor: int
    experience_bonus_limit: int
    kamas: int
    alignment_information: AlignmentInformation
    critical_hit_weapon: int
    characteristics: _containers.RepeatedCompositeFieldContainer[CharacterCharacteristic]
    spell_modifiers: _containers.RepeatedCompositeFieldContainer[SpellModifier]
    probation_time: int
    def __init__(self, experience: _Optional[int] = ..., experience_level_floor: _Optional[int] = ..., experience_next_level_floor: _Optional[int] = ..., experience_bonus_limit: _Optional[int] = ..., kamas: _Optional[int] = ..., alignment_information: _Optional[_Union[AlignmentInformation, _Mapping]] = ..., critical_hit_weapon: _Optional[int] = ..., characteristics: _Optional[_Iterable[_Union[CharacterCharacteristic, _Mapping]]] = ..., spell_modifiers: _Optional[_Iterable[_Union[SpellModifier, _Mapping]]] = ..., probation_time: _Optional[int] = ...) -> None: ...

class AlignmentInformation(_message.Message):
    __slots__ = ("alignment", "alignment_quest_number", "alignment_grade", "character_id", "character_level", "extended_information")
    class AlignmentExtendedInformation(_message.Message):
        __slots__ = ("honor", "honor_grade_floor", "honor_next_grade_floor", "attackable")
        HONOR_FIELD_NUMBER: _ClassVar[int]
        HONOR_GRADE_FLOOR_FIELD_NUMBER: _ClassVar[int]
        HONOR_NEXT_GRADE_FLOOR_FIELD_NUMBER: _ClassVar[int]
        ATTACKABLE_FIELD_NUMBER: _ClassVar[int]
        honor: int
        honor_grade_floor: int
        honor_next_grade_floor: int
        attackable: AttackableStatus
        def __init__(self, honor: _Optional[int] = ..., honor_grade_floor: _Optional[int] = ..., honor_next_grade_floor: _Optional[int] = ..., attackable: _Optional[_Union[AttackableStatus, str]] = ...) -> None: ...
    ALIGNMENT_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_QUEST_NUMBER_FIELD_NUMBER: _ClassVar[int]
    ALIGNMENT_GRADE_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_LEVEL_FIELD_NUMBER: _ClassVar[int]
    EXTENDED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    alignment: Alignment
    alignment_quest_number: int
    alignment_grade: int
    character_id: int
    character_level: int
    extended_information: AlignmentInformation.AlignmentExtendedInformation
    def __init__(self, alignment: _Optional[_Union[Alignment, str]] = ..., alignment_quest_number: _Optional[int] = ..., alignment_grade: _Optional[int] = ..., character_id: _Optional[int] = ..., character_level: _Optional[int] = ..., extended_information: _Optional[_Union[AlignmentInformation.AlignmentExtendedInformation, _Mapping]] = ...) -> None: ...

class InteractiveElement(_message.Message):
    __slots__ = ("element_id", "element_type_id", "enabled_skills", "disabled_skills", "on_current_map", "age_bonus")
    class InteractiveElementSkill(_message.Message):
        __slots__ = ("skill_id", "skill_instance_uid", "name_id")
        SKILL_ID_FIELD_NUMBER: _ClassVar[int]
        SKILL_INSTANCE_UID_FIELD_NUMBER: _ClassVar[int]
        NAME_ID_FIELD_NUMBER: _ClassVar[int]
        skill_id: int
        skill_instance_uid: int
        name_id: int
        def __init__(self, skill_id: _Optional[int] = ..., skill_instance_uid: _Optional[int] = ..., name_id: _Optional[int] = ...) -> None: ...
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    ELEMENT_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLED_SKILLS_FIELD_NUMBER: _ClassVar[int]
    DISABLED_SKILLS_FIELD_NUMBER: _ClassVar[int]
    ON_CURRENT_MAP_FIELD_NUMBER: _ClassVar[int]
    AGE_BONUS_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    element_type_id: int
    enabled_skills: _containers.RepeatedCompositeFieldContainer[InteractiveElement.InteractiveElementSkill]
    disabled_skills: _containers.RepeatedCompositeFieldContainer[InteractiveElement.InteractiveElementSkill]
    on_current_map: bool
    age_bonus: int
    def __init__(self, element_id: _Optional[int] = ..., element_type_id: _Optional[int] = ..., enabled_skills: _Optional[_Iterable[_Union[InteractiveElement.InteractiveElementSkill, _Mapping]]] = ..., disabled_skills: _Optional[_Iterable[_Union[InteractiveElement.InteractiveElementSkill, _Mapping]]] = ..., on_current_map: bool = ..., age_bonus: _Optional[int] = ...) -> None: ...

class StatedElement(_message.Message):
    __slots__ = ("element_id", "cell_id", "state", "on_current_map")
    ELEMENT_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ON_CURRENT_MAP_FIELD_NUMBER: _ClassVar[int]
    element_id: int
    cell_id: int
    state: int
    on_current_map: bool
    def __init__(self, element_id: _Optional[int] = ..., cell_id: _Optional[int] = ..., state: _Optional[int] = ..., on_current_map: bool = ...) -> None: ...

class EntityLook(_message.Message):
    __slots__ = ("bones_id", "skins", "indexed_colors", "scales", "sub_entities")
    BONES_ID_FIELD_NUMBER: _ClassVar[int]
    SKINS_FIELD_NUMBER: _ClassVar[int]
    INDEXED_COLORS_FIELD_NUMBER: _ClassVar[int]
    SCALES_FIELD_NUMBER: _ClassVar[int]
    SUB_ENTITIES_FIELD_NUMBER: _ClassVar[int]
    bones_id: int
    skins: _containers.RepeatedScalarFieldContainer[int]
    indexed_colors: _containers.RepeatedScalarFieldContainer[int]
    scales: _containers.RepeatedScalarFieldContainer[int]
    sub_entities: _containers.RepeatedCompositeFieldContainer[SubEntityInformation]
    def __init__(self, bones_id: _Optional[int] = ..., skins: _Optional[_Iterable[int]] = ..., indexed_colors: _Optional[_Iterable[int]] = ..., scales: _Optional[_Iterable[int]] = ..., sub_entities: _Optional[_Iterable[_Union[SubEntityInformation, _Mapping]]] = ...) -> None: ...

class SubEntityInformation(_message.Message):
    __slots__ = ("binding_point_category", "binding_point_index", "sub_entity_look")
    class BindingPointCategoryEnum(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        HOOK_POINT_CATEGORY_UNUSED: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_PET: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_MOUNT_DRIVER: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_LIFTED_ENTITY: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_BASE_BACKGROUND: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_BASE_FOREGROUND: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
        HOOK_POINT_CATEGORY_UNDERWATER_BUBBLES: _ClassVar[SubEntityInformation.BindingPointCategoryEnum]
    HOOK_POINT_CATEGORY_UNUSED: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_PET: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_MOUNT_DRIVER: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_LIFTED_ENTITY: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_BASE_BACKGROUND: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_BASE_FOREGROUND: SubEntityInformation.BindingPointCategoryEnum
    HOOK_POINT_CATEGORY_UNDERWATER_BUBBLES: SubEntityInformation.BindingPointCategoryEnum
    BINDING_POINT_CATEGORY_FIELD_NUMBER: _ClassVar[int]
    BINDING_POINT_INDEX_FIELD_NUMBER: _ClassVar[int]
    SUB_ENTITY_LOOK_FIELD_NUMBER: _ClassVar[int]
    binding_point_category: SubEntityInformation.BindingPointCategoryEnum
    binding_point_index: int
    sub_entity_look: EntityLook
    def __init__(self, binding_point_category: _Optional[_Union[SubEntityInformation.BindingPointCategoryEnum, str]] = ..., binding_point_index: _Optional[int] = ..., sub_entity_look: _Optional[_Union[EntityLook, _Mapping]] = ...) -> None: ...

class EntityDisposition(_message.Message):
    __slots__ = ("entity_id", "cell_id", "direction", "carrying_character_id")
    ENTITY_ID_FIELD_NUMBER: _ClassVar[int]
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    DIRECTION_FIELD_NUMBER: _ClassVar[int]
    CARRYING_CHARACTER_ID_FIELD_NUMBER: _ClassVar[int]
    entity_id: int
    cell_id: int
    direction: Direction
    carrying_character_id: int
    def __init__(self, entity_id: _Optional[int] = ..., cell_id: _Optional[int] = ..., direction: _Optional[_Union[Direction, str]] = ..., carrying_character_id: _Optional[int] = ...) -> None: ...

class NamedPartyTeam(_message.Message):
    __slots__ = ("team", "party_name")
    TEAM_FIELD_NUMBER: _ClassVar[int]
    PARTY_NAME_FIELD_NUMBER: _ClassVar[int]
    team: Team
    party_name: str
    def __init__(self, team: _Optional[_Union[Team, str]] = ..., party_name: _Optional[str] = ...) -> None: ...

class SocialFightInformation(_message.Message):
    __slots__ = ("fight_id", "fight_type", "map_id")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        TAX_COLLECTOR: _ClassVar[SocialFightInformation.Type]
        PRISM: _ClassVar[SocialFightInformation.Type]
    TAX_COLLECTOR: SocialFightInformation.Type
    PRISM: SocialFightInformation.Type
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_TYPE_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    fight_type: SocialFightInformation.Type
    map_id: int
    def __init__(self, fight_id: _Optional[int] = ..., fight_type: _Optional[_Union[SocialFightInformation.Type, str]] = ..., map_id: _Optional[int] = ...) -> None: ...

class SocialFight(_message.Message):
    __slots__ = ("social_fight_info", "attackers", "defenders", "phase")
    SOCIAL_FIGHT_INFO_FIELD_NUMBER: _ClassVar[int]
    ATTACKERS_FIELD_NUMBER: _ClassVar[int]
    DEFENDERS_FIELD_NUMBER: _ClassVar[int]
    PHASE_FIELD_NUMBER: _ClassVar[int]
    social_fight_info: SocialFightInformation
    attackers: _containers.RepeatedCompositeFieldContainer[Character]
    defenders: _containers.RepeatedCompositeFieldContainer[Character]
    phase: FightPhaseInfo
    def __init__(self, social_fight_info: _Optional[_Union[SocialFightInformation, _Mapping]] = ..., attackers: _Optional[_Iterable[_Union[Character, _Mapping]]] = ..., defenders: _Optional[_Iterable[_Union[Character, _Mapping]]] = ..., phase: _Optional[_Union[FightPhaseInfo, _Mapping]] = ...) -> None: ...

class FightPhaseInfo(_message.Message):
    __slots__ = ("phase", "phase_end_timestamp")
    class FightPhase(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        STARTED: _ClassVar[FightPhaseInfo.FightPhase]
        JOINING_PHASE: _ClassVar[FightPhaseInfo.FightPhase]
        POSITIONING_PHASE: _ClassVar[FightPhaseInfo.FightPhase]
    STARTED: FightPhaseInfo.FightPhase
    JOINING_PHASE: FightPhaseInfo.FightPhase
    POSITIONING_PHASE: FightPhaseInfo.FightPhase
    PHASE_FIELD_NUMBER: _ClassVar[int]
    PHASE_END_TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    phase: FightPhaseInfo.FightPhase
    phase_end_timestamp: int
    def __init__(self, phase: _Optional[_Union[FightPhaseInfo.FightPhase, str]] = ..., phase_end_timestamp: _Optional[int] = ...) -> None: ...

class FightOptionsInformation(_message.Message):
    __slots__ = ("is_secret", "is_restricted_to_party", "is_closed", "is_asking_for_help")
    IS_SECRET_FIELD_NUMBER: _ClassVar[int]
    IS_RESTRICTED_TO_PARTY_FIELD_NUMBER: _ClassVar[int]
    IS_CLOSED_FIELD_NUMBER: _ClassVar[int]
    IS_ASKING_FOR_HELP_FIELD_NUMBER: _ClassVar[int]
    is_secret: bool
    is_restricted_to_party: bool
    is_closed: bool
    is_asking_for_help: bool
    def __init__(self, is_secret: bool = ..., is_restricted_to_party: bool = ..., is_closed: bool = ..., is_asking_for_help: bool = ...) -> None: ...

class FighterLightInformation(_message.Message):
    __slots__ = ("id", "wave", "level", "breed_id", "gender", "alive", "monster_information", "entity_information", "tax_collector_information", "named_information")
    ID_FIELD_NUMBER: _ClassVar[int]
    WAVE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    BREED_ID_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    ALIVE_FIELD_NUMBER: _ClassVar[int]
    MONSTER_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ENTITY_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTOR_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    NAMED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    wave: int
    level: int
    breed_id: int
    gender: Gender
    alive: bool
    monster_information: FighterMonsterLightInformation
    entity_information: FighterEntityLightInformation
    tax_collector_information: FighterTaxCollectorLightInformation
    named_information: FighterNamedLightInformation
    def __init__(self, id: _Optional[int] = ..., wave: _Optional[int] = ..., level: _Optional[int] = ..., breed_id: _Optional[int] = ..., gender: _Optional[_Union[Gender, str]] = ..., alive: bool = ..., monster_information: _Optional[_Union[FighterMonsterLightInformation, _Mapping]] = ..., entity_information: _Optional[_Union[FighterEntityLightInformation, _Mapping]] = ..., tax_collector_information: _Optional[_Union[FighterTaxCollectorLightInformation, _Mapping]] = ..., named_information: _Optional[_Union[FighterNamedLightInformation, _Mapping]] = ...) -> None: ...

class FighterMonsterLightInformation(_message.Message):
    __slots__ = ("monster_gid",)
    MONSTER_GID_FIELD_NUMBER: _ClassVar[int]
    monster_gid: int
    def __init__(self, monster_gid: _Optional[int] = ...) -> None: ...

class FighterEntityLightInformation(_message.Message):
    __slots__ = ("entity_model_id", "master_id")
    ENTITY_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    entity_model_id: int
    master_id: int
    def __init__(self, entity_model_id: _Optional[int] = ..., master_id: _Optional[int] = ...) -> None: ...

class FighterTaxCollectorLightInformation(_message.Message):
    __slots__ = ("first_name_id", "last_name_id")
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    first_name_id: int
    last_name_id: int
    def __init__(self, first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ...) -> None: ...

class FighterNamedLightInformation(_message.Message):
    __slots__ = ("name",)
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class FightCommonInformation(_message.Message):
    __slots__ = ("fight_id", "type", "teams_information", "teams_position", "teams_options")
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    TEAMS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    TEAMS_POSITION_FIELD_NUMBER: _ClassVar[int]
    TEAMS_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    type: FightType
    teams_information: _containers.RepeatedCompositeFieldContainer[FightTeamInformation]
    teams_position: _containers.RepeatedScalarFieldContainer[int]
    teams_options: _containers.RepeatedCompositeFieldContainer[FightOptionsInformation]
    def __init__(self, fight_id: _Optional[int] = ..., type: _Optional[_Union[FightType, str]] = ..., teams_information: _Optional[_Iterable[_Union[FightTeamInformation, _Mapping]]] = ..., teams_position: _Optional[_Iterable[int]] = ..., teams_options: _Optional[_Iterable[_Union[FightOptionsInformation, _Mapping]]] = ...) -> None: ...

class FightTeamInformation(_message.Message):
    __slots__ = ("team", "leader_id", "side", "type", "waves", "team_members", "light_information")
    TEAM_FIELD_NUMBER: _ClassVar[int]
    LEADER_ID_FIELD_NUMBER: _ClassVar[int]
    SIDE_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    WAVES_FIELD_NUMBER: _ClassVar[int]
    TEAM_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    LIGHT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    team: Team
    leader_id: int
    side: Alignment
    type: TeamType
    waves: int
    team_members: FightTeamMembersInformation
    light_information: FightTeamLightInformation
    def __init__(self, team: _Optional[_Union[Team, str]] = ..., leader_id: _Optional[int] = ..., side: _Optional[_Union[Alignment, str]] = ..., type: _Optional[_Union[TeamType, str]] = ..., waves: _Optional[int] = ..., team_members: _Optional[_Union[FightTeamMembersInformation, _Mapping]] = ..., light_information: _Optional[_Union[FightTeamLightInformation, _Mapping]] = ...) -> None: ...

class FightExternalInformation(_message.Message):
    __slots__ = ("fight_id", "fight_type", "fight_start", "fight_spectator_locked", "fight_teams_with_options")
    class FightTeamsWithOptions(_message.Message):
        __slots__ = ("fight_team", "fight_team_options")
        FIGHT_TEAM_FIELD_NUMBER: _ClassVar[int]
        FIGHT_TEAM_OPTIONS_FIELD_NUMBER: _ClassVar[int]
        fight_team: FightTeamInformation
        fight_team_options: FightOptionsInformation
        def __init__(self, fight_team: _Optional[_Union[FightTeamInformation, _Mapping]] = ..., fight_team_options: _Optional[_Union[FightOptionsInformation, _Mapping]] = ...) -> None: ...
    FIGHT_ID_FIELD_NUMBER: _ClassVar[int]
    FIGHT_TYPE_FIELD_NUMBER: _ClassVar[int]
    FIGHT_START_FIELD_NUMBER: _ClassVar[int]
    FIGHT_SPECTATOR_LOCKED_FIELD_NUMBER: _ClassVar[int]
    FIGHT_TEAMS_WITH_OPTIONS_FIELD_NUMBER: _ClassVar[int]
    fight_id: int
    fight_type: FightType
    fight_start: int
    fight_spectator_locked: bool
    fight_teams_with_options: _containers.RepeatedCompositeFieldContainer[FightExternalInformation.FightTeamsWithOptions]
    def __init__(self, fight_id: _Optional[int] = ..., fight_type: _Optional[_Union[FightType, str]] = ..., fight_start: _Optional[int] = ..., fight_spectator_locked: bool = ..., fight_teams_with_options: _Optional[_Iterable[_Union[FightExternalInformation.FightTeamsWithOptions, _Mapping]]] = ...) -> None: ...

class FightTeamLightInformation(_message.Message):
    __slots__ = ("team_members_count", "average_level", "has_friend", "has_guild_member", "has_alliance_member", "has_group_member", "has_my_tax_collector")
    TEAM_MEMBERS_COUNT_FIELD_NUMBER: _ClassVar[int]
    AVERAGE_LEVEL_FIELD_NUMBER: _ClassVar[int]
    HAS_FRIEND_FIELD_NUMBER: _ClassVar[int]
    HAS_GUILD_MEMBER_FIELD_NUMBER: _ClassVar[int]
    HAS_ALLIANCE_MEMBER_FIELD_NUMBER: _ClassVar[int]
    HAS_GROUP_MEMBER_FIELD_NUMBER: _ClassVar[int]
    HAS_MY_TAX_COLLECTOR_FIELD_NUMBER: _ClassVar[int]
    team_members_count: int
    average_level: int
    has_friend: bool
    has_guild_member: bool
    has_alliance_member: bool
    has_group_member: bool
    has_my_tax_collector: bool
    def __init__(self, team_members_count: _Optional[int] = ..., average_level: _Optional[int] = ..., has_friend: bool = ..., has_guild_member: bool = ..., has_alliance_member: bool = ..., has_group_member: bool = ..., has_my_tax_collector: bool = ...) -> None: ...

class FightTeamMembersInformation(_message.Message):
    __slots__ = ("team_members", "alliance_relation")
    TEAM_MEMBERS_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_RELATION_FIELD_NUMBER: _ClassVar[int]
    team_members: _containers.RepeatedCompositeFieldContainer[FightTeamMemberInformation]
    alliance_relation: AllianceRelation
    def __init__(self, team_members: _Optional[_Iterable[_Union[FightTeamMemberInformation, _Mapping]]] = ..., alliance_relation: _Optional[_Union[AllianceRelation, str]] = ...) -> None: ...

class FightTeamMemberInformation(_message.Message):
    __slots__ = ("member_id", "character_member", "entity_member", "monster_member", "tax_collector_member")
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_MEMBER_FIELD_NUMBER: _ClassVar[int]
    ENTITY_MEMBER_FIELD_NUMBER: _ClassVar[int]
    MONSTER_MEMBER_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTOR_MEMBER_FIELD_NUMBER: _ClassVar[int]
    member_id: int
    character_member: FightTeamMemberCharacter
    entity_member: FightTeamMemberEntity
    monster_member: FightTeamMemberMonster
    tax_collector_member: FightTeamMemberTaxCollector
    def __init__(self, member_id: _Optional[int] = ..., character_member: _Optional[_Union[FightTeamMemberCharacter, _Mapping]] = ..., entity_member: _Optional[_Union[FightTeamMemberEntity, _Mapping]] = ..., monster_member: _Optional[_Union[FightTeamMemberMonster, _Mapping]] = ..., tax_collector_member: _Optional[_Union[FightTeamMemberTaxCollector, _Mapping]] = ...) -> None: ...

class FightTeamMemberCharacter(_message.Message):
    __slots__ = ("name", "level", "alliance_info")
    class BasicAllianceInformation(_message.Message):
        __slots__ = ("alliance_uid", "alliance_tag")
        ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
        ALLIANCE_TAG_FIELD_NUMBER: _ClassVar[int]
        alliance_uid: str
        alliance_tag: str
        def __init__(self, alliance_uid: _Optional[str] = ..., alliance_tag: _Optional[str] = ...) -> None: ...
    NAME_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_INFO_FIELD_NUMBER: _ClassVar[int]
    name: str
    level: int
    alliance_info: FightTeamMemberCharacter.BasicAllianceInformation
    def __init__(self, name: _Optional[str] = ..., level: _Optional[int] = ..., alliance_info: _Optional[_Union[FightTeamMemberCharacter.BasicAllianceInformation, _Mapping]] = ...) -> None: ...

class FightTeamMemberEntity(_message.Message):
    __slots__ = ("entity_model_id", "level", "master_id")
    ENTITY_MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    MASTER_ID_FIELD_NUMBER: _ClassVar[int]
    entity_model_id: int
    level: int
    master_id: int
    def __init__(self, entity_model_id: _Optional[int] = ..., level: _Optional[int] = ..., master_id: _Optional[int] = ...) -> None: ...

class FightTeamMemberMonster(_message.Message):
    __slots__ = ("monster_id", "grade")
    MONSTER_ID_FIELD_NUMBER: _ClassVar[int]
    GRADE_FIELD_NUMBER: _ClassVar[int]
    monster_id: int
    grade: int
    def __init__(self, monster_id: _Optional[int] = ..., grade: _Optional[int] = ...) -> None: ...

class FightTeamMemberTaxCollector(_message.Message):
    __slots__ = ("first_name_id", "last_name_id", "group_id", "tax_collector_uid")
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    GROUP_ID_FIELD_NUMBER: _ClassVar[int]
    TAX_COLLECTOR_UID_FIELD_NUMBER: _ClassVar[int]
    first_name_id: int
    last_name_id: int
    group_id: int
    tax_collector_uid: str
    def __init__(self, first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., group_id: _Optional[int] = ..., tax_collector_uid: _Optional[str] = ...) -> None: ...

class FightStartingPositions(_message.Message):
    __slots__ = ("challengers_positions", "defenders_positions")
    CHALLENGERS_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    DEFENDERS_POSITIONS_FIELD_NUMBER: _ClassVar[int]
    challengers_positions: _containers.RepeatedScalarFieldContainer[int]
    defenders_positions: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, challengers_positions: _Optional[_Iterable[int]] = ..., defenders_positions: _Optional[_Iterable[int]] = ...) -> None: ...

class FightRemovableEffectExtendedInformation(_message.Message):
    __slots__ = ("action_id", "source_id", "effect")
    ACTION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_ID_FIELD_NUMBER: _ClassVar[int]
    EFFECT_FIELD_NUMBER: _ClassVar[int]
    action_id: int
    source_id: int
    effect: FightRemovableEffect
    def __init__(self, action_id: _Optional[int] = ..., source_id: _Optional[int] = ..., effect: _Optional[_Union[FightRemovableEffect, _Mapping]] = ...) -> None: ...

class FightRemovableEffect(_message.Message):
    __slots__ = ("uid", "target_id", "turn_duration", "dissipation_state", "spell_id", "effect_id", "parent_boost_id", "temporary_boost_effect", "temporary_spell_immunity_effect", "triggered_effect")
    class EffectDissipationState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        DISSIPATED: _ClassVar[FightRemovableEffect.EffectDissipationState]
        DISSIPATED_BY_DEATH: _ClassVar[FightRemovableEffect.EffectDissipationState]
        DISSIPATED_BY_STRONG_DISPEL: _ClassVar[FightRemovableEffect.EffectDissipationState]
        REALLY_NOT_DISSIPATED: _ClassVar[FightRemovableEffect.EffectDissipationState]
    DISSIPATED: FightRemovableEffect.EffectDissipationState
    DISSIPATED_BY_DEATH: FightRemovableEffect.EffectDissipationState
    DISSIPATED_BY_STRONG_DISPEL: FightRemovableEffect.EffectDissipationState
    REALLY_NOT_DISSIPATED: FightRemovableEffect.EffectDissipationState
    UID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    TURN_DURATION_FIELD_NUMBER: _ClassVar[int]
    DISSIPATION_STATE_FIELD_NUMBER: _ClassVar[int]
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
    PARENT_BOOST_ID_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_BOOST_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TEMPORARY_SPELL_IMMUNITY_EFFECT_FIELD_NUMBER: _ClassVar[int]
    TRIGGERED_EFFECT_FIELD_NUMBER: _ClassVar[int]
    uid: int
    target_id: int
    turn_duration: int
    dissipation_state: FightRemovableEffect.EffectDissipationState
    spell_id: int
    effect_id: int
    parent_boost_id: int
    temporary_boost_effect: FightTemporaryBoostEffect
    temporary_spell_immunity_effect: FightTemporarySpellImmunityEffect
    triggered_effect: FightTriggeredEffect
    def __init__(self, uid: _Optional[int] = ..., target_id: _Optional[int] = ..., turn_duration: _Optional[int] = ..., dissipation_state: _Optional[_Union[FightRemovableEffect.EffectDissipationState, str]] = ..., spell_id: _Optional[int] = ..., effect_id: _Optional[int] = ..., parent_boost_id: _Optional[int] = ..., temporary_boost_effect: _Optional[_Union[FightTemporaryBoostEffect, _Mapping]] = ..., temporary_spell_immunity_effect: _Optional[_Union[FightTemporarySpellImmunityEffect, _Mapping]] = ..., triggered_effect: _Optional[_Union[FightTriggeredEffect, _Mapping]] = ...) -> None: ...

class FightTemporaryBoostEffect(_message.Message):
    __slots__ = ("delta", "boosted_spell_id", "weapon_type_id", "state_id", "details")
    class Details(_message.Message):
        __slots__ = ("first_param", "second_param", "third_param")
        FIRST_PARAM_FIELD_NUMBER: _ClassVar[int]
        SECOND_PARAM_FIELD_NUMBER: _ClassVar[int]
        THIRD_PARAM_FIELD_NUMBER: _ClassVar[int]
        first_param: int
        second_param: int
        third_param: int
        def __init__(self, first_param: _Optional[int] = ..., second_param: _Optional[int] = ..., third_param: _Optional[int] = ...) -> None: ...
    DELTA_FIELD_NUMBER: _ClassVar[int]
    BOOSTED_SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    WEAPON_TYPE_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_ID_FIELD_NUMBER: _ClassVar[int]
    DETAILS_FIELD_NUMBER: _ClassVar[int]
    delta: int
    boosted_spell_id: int
    weapon_type_id: int
    state_id: int
    details: FightTemporaryBoostEffect.Details
    def __init__(self, delta: _Optional[int] = ..., boosted_spell_id: _Optional[int] = ..., weapon_type_id: _Optional[int] = ..., state_id: _Optional[int] = ..., details: _Optional[_Union[FightTemporaryBoostEffect.Details, _Mapping]] = ...) -> None: ...

class FightTemporarySpellImmunityEffect(_message.Message):
    __slots__ = ("immune_spell_id",)
    IMMUNE_SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    immune_spell_id: int
    def __init__(self, immune_spell_id: _Optional[int] = ...) -> None: ...

class FightTriggeredEffect(_message.Message):
    __slots__ = ("first_param", "second_param", "third_param", "delay")
    FIRST_PARAM_FIELD_NUMBER: _ClassVar[int]
    SECOND_PARAM_FIELD_NUMBER: _ClassVar[int]
    THIRD_PARAM_FIELD_NUMBER: _ClassVar[int]
    DELAY_FIELD_NUMBER: _ClassVar[int]
    first_param: int
    second_param: int
    third_param: int
    delay: int
    def __init__(self, first_param: _Optional[int] = ..., second_param: _Optional[int] = ..., third_param: _Optional[int] = ..., delay: _Optional[int] = ...) -> None: ...

class FightMark(_message.Message):
    __slots__ = ("author_id", "team", "spell_id", "spell_level", "mark_id", "mark_type", "mark_impact_cell", "cells", "active")
    class MarkType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        GLYPH: _ClassVar[FightMark.MarkType]
        TRAP: _ClassVar[FightMark.MarkType]
        WALL: _ClassVar[FightMark.MarkType]
        PORTAL: _ClassVar[FightMark.MarkType]
        RUNE: _ClassVar[FightMark.MarkType]
    GLYPH: FightMark.MarkType
    TRAP: FightMark.MarkType
    WALL: FightMark.MarkType
    PORTAL: FightMark.MarkType
    RUNE: FightMark.MarkType
    class MarkedCell(_message.Message):
        __slots__ = ("id", "zone_size", "color", "cells_type")
        class MarkCellsType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CELLS_CIRCLE: _ClassVar[FightMark.MarkedCell.MarkCellsType]
            CELLS_CROSS: _ClassVar[FightMark.MarkedCell.MarkCellsType]
            CELLS_SQUARE: _ClassVar[FightMark.MarkedCell.MarkCellsType]
        CELLS_CIRCLE: FightMark.MarkedCell.MarkCellsType
        CELLS_CROSS: FightMark.MarkedCell.MarkCellsType
        CELLS_SQUARE: FightMark.MarkedCell.MarkCellsType
        ID_FIELD_NUMBER: _ClassVar[int]
        ZONE_SIZE_FIELD_NUMBER: _ClassVar[int]
        COLOR_FIELD_NUMBER: _ClassVar[int]
        CELLS_TYPE_FIELD_NUMBER: _ClassVar[int]
        id: int
        zone_size: int
        color: int
        cells_type: FightMark.MarkedCell.MarkCellsType
        def __init__(self, id: _Optional[int] = ..., zone_size: _Optional[int] = ..., color: _Optional[int] = ..., cells_type: _Optional[_Union[FightMark.MarkedCell.MarkCellsType, str]] = ...) -> None: ...
    AUTHOR_ID_FIELD_NUMBER: _ClassVar[int]
    TEAM_FIELD_NUMBER: _ClassVar[int]
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MARK_ID_FIELD_NUMBER: _ClassVar[int]
    MARK_TYPE_FIELD_NUMBER: _ClassVar[int]
    MARK_IMPACT_CELL_FIELD_NUMBER: _ClassVar[int]
    CELLS_FIELD_NUMBER: _ClassVar[int]
    ACTIVE_FIELD_NUMBER: _ClassVar[int]
    author_id: int
    team: Team
    spell_id: int
    spell_level: int
    mark_id: int
    mark_type: FightMark.MarkType
    mark_impact_cell: int
    cells: _containers.RepeatedCompositeFieldContainer[FightMark.MarkedCell]
    active: bool
    def __init__(self, author_id: _Optional[int] = ..., team: _Optional[_Union[Team, str]] = ..., spell_id: _Optional[int] = ..., spell_level: _Optional[int] = ..., mark_id: _Optional[int] = ..., mark_type: _Optional[_Union[FightMark.MarkType, str]] = ..., mark_impact_cell: _Optional[int] = ..., cells: _Optional[_Iterable[_Union[FightMark.MarkedCell, _Mapping]]] = ..., active: bool = ...) -> None: ...

class FightEffectTriggerCount(_message.Message):
    __slots__ = ("effect_id", "target_id", "count")
    EFFECT_ID_FIELD_NUMBER: _ClassVar[int]
    TARGET_ID_FIELD_NUMBER: _ClassVar[int]
    COUNT_FIELD_NUMBER: _ClassVar[int]
    effect_id: int
    target_id: int
    count: int
    def __init__(self, effect_id: _Optional[int] = ..., target_id: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...

class FightSpellCoolDown(_message.Message):
    __slots__ = ("spell_id", "cool_down")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    COOL_DOWN_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    cool_down: int
    def __init__(self, spell_id: _Optional[int] = ..., cool_down: _Optional[int] = ...) -> None: ...

class FightResumeSlaves(_message.Message):
    __slots__ = ("slave_id", "spell_cool_downs", "summon_count", "bomb_count")
    SLAVE_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_COOL_DOWNS_FIELD_NUMBER: _ClassVar[int]
    SUMMON_COUNT_FIELD_NUMBER: _ClassVar[int]
    BOMB_COUNT_FIELD_NUMBER: _ClassVar[int]
    slave_id: int
    spell_cool_downs: _containers.RepeatedCompositeFieldContainer[FightSpellCoolDown]
    summon_count: int
    bomb_count: int
    def __init__(self, slave_id: _Optional[int] = ..., spell_cool_downs: _Optional[_Iterable[_Union[FightSpellCoolDown, _Mapping]]] = ..., summon_count: _Optional[int] = ..., bomb_count: _Optional[int] = ...) -> None: ...

class FightResultListEntry(_message.Message):
    __slots__ = ("outcome", "wave", "rewards", "fighter_list_entry")
    class FightLoot(_message.Message):
        __slots__ = ("objects", "kamas")
        class Object(_message.Message):
            __slots__ = ("id", "quantity", "priority_hint")
            ID_FIELD_NUMBER: _ClassVar[int]
            QUANTITY_FIELD_NUMBER: _ClassVar[int]
            PRIORITY_HINT_FIELD_NUMBER: _ClassVar[int]
            id: int
            quantity: int
            priority_hint: int
            def __init__(self, id: _Optional[int] = ..., quantity: _Optional[int] = ..., priority_hint: _Optional[int] = ...) -> None: ...
        OBJECTS_FIELD_NUMBER: _ClassVar[int]
        KAMAS_FIELD_NUMBER: _ClassVar[int]
        objects: _containers.RepeatedCompositeFieldContainer[FightResultListEntry.FightLoot.Object]
        kamas: int
        def __init__(self, objects: _Optional[_Iterable[_Union[FightResultListEntry.FightLoot.Object, _Mapping]]] = ..., kamas: _Optional[int] = ...) -> None: ...
    class FighterListEntry(_message.Message):
        __slots__ = ("fighter_id", "alive", "player_list_entry", "mutant_list_entry", "tax_collector_list_entry")
        class PlayerListEntry(_message.Message):
            __slots__ = ("level", "additional")
            class FightResultAdditionalData(_message.Message):
                __slots__ = ("experience_data", "pvp_data")
                class ExperienceData(_message.Message):
                    __slots__ = ("experience", "show_experience", "experience_level_floor", "show_experience_level_floor", "experience_next_level_floor", "show_experience_next_level_floor", "experience_fight_delta", "show_experience_fight_delta", "experience_for_guild", "show_experience_for_guild", "experience_for_mount", "show_experience_for_mount", "re_roll_experience_multiplier")
                    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
                    EXPERIENCE_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
                    EXPERIENCE_NEXT_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_NEXT_LEVEL_FLOOR_FIELD_NUMBER: _ClassVar[int]
                    EXPERIENCE_FIGHT_DELTA_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_FIGHT_DELTA_FIELD_NUMBER: _ClassVar[int]
                    EXPERIENCE_FOR_GUILD_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_FOR_GUILD_FIELD_NUMBER: _ClassVar[int]
                    EXPERIENCE_FOR_MOUNT_FIELD_NUMBER: _ClassVar[int]
                    SHOW_EXPERIENCE_FOR_MOUNT_FIELD_NUMBER: _ClassVar[int]
                    RE_ROLL_EXPERIENCE_MULTIPLIER_FIELD_NUMBER: _ClassVar[int]
                    experience: int
                    show_experience: bool
                    experience_level_floor: int
                    show_experience_level_floor: bool
                    experience_next_level_floor: int
                    show_experience_next_level_floor: bool
                    experience_fight_delta: int
                    show_experience_fight_delta: bool
                    experience_for_guild: int
                    show_experience_for_guild: bool
                    experience_for_mount: int
                    show_experience_for_mount: bool
                    re_roll_experience_multiplier: int
                    def __init__(self, experience: _Optional[int] = ..., show_experience: bool = ..., experience_level_floor: _Optional[int] = ..., show_experience_level_floor: bool = ..., experience_next_level_floor: _Optional[int] = ..., show_experience_next_level_floor: bool = ..., experience_fight_delta: _Optional[int] = ..., show_experience_fight_delta: bool = ..., experience_for_guild: _Optional[int] = ..., show_experience_for_guild: bool = ..., experience_for_mount: _Optional[int] = ..., show_experience_for_mount: bool = ..., re_roll_experience_multiplier: _Optional[int] = ...) -> None: ...
                class PvpData(_message.Message):
                    __slots__ = ("grade", "min_honor_for_grade", "max_honor_for_grade", "honor", "honor_delta")
                    GRADE_FIELD_NUMBER: _ClassVar[int]
                    MIN_HONOR_FOR_GRADE_FIELD_NUMBER: _ClassVar[int]
                    MAX_HONOR_FOR_GRADE_FIELD_NUMBER: _ClassVar[int]
                    HONOR_FIELD_NUMBER: _ClassVar[int]
                    HONOR_DELTA_FIELD_NUMBER: _ClassVar[int]
                    grade: int
                    min_honor_for_grade: int
                    max_honor_for_grade: int
                    honor: int
                    honor_delta: int
                    def __init__(self, grade: _Optional[int] = ..., min_honor_for_grade: _Optional[int] = ..., max_honor_for_grade: _Optional[int] = ..., honor: _Optional[int] = ..., honor_delta: _Optional[int] = ...) -> None: ...
                EXPERIENCE_DATA_FIELD_NUMBER: _ClassVar[int]
                PVP_DATA_FIELD_NUMBER: _ClassVar[int]
                experience_data: FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.ExperienceData
                pvp_data: FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.PvpData
                def __init__(self, experience_data: _Optional[_Union[FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.ExperienceData, _Mapping]] = ..., pvp_data: _Optional[_Union[FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData.PvpData, _Mapping]] = ...) -> None: ...
            LEVEL_FIELD_NUMBER: _ClassVar[int]
            ADDITIONAL_FIELD_NUMBER: _ClassVar[int]
            level: int
            additional: _containers.RepeatedCompositeFieldContainer[FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData]
            def __init__(self, level: _Optional[int] = ..., additional: _Optional[_Iterable[_Union[FightResultListEntry.FighterListEntry.PlayerListEntry.FightResultAdditionalData, _Mapping]]] = ...) -> None: ...
        class MutantListEntry(_message.Message):
            __slots__ = ("level",)
            LEVEL_FIELD_NUMBER: _ClassVar[int]
            level: int
            def __init__(self, level: _Optional[int] = ...) -> None: ...
        class TaxCollectorListEntry(_message.Message):
            __slots__ = ("alliance_information",)
            ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            alliance_information: AllianceInformation
            def __init__(self, alliance_information: _Optional[_Union[AllianceInformation, _Mapping]] = ...) -> None: ...
        FIGHTER_ID_FIELD_NUMBER: _ClassVar[int]
        ALIVE_FIELD_NUMBER: _ClassVar[int]
        PLAYER_LIST_ENTRY_FIELD_NUMBER: _ClassVar[int]
        MUTANT_LIST_ENTRY_FIELD_NUMBER: _ClassVar[int]
        TAX_COLLECTOR_LIST_ENTRY_FIELD_NUMBER: _ClassVar[int]
        fighter_id: int
        alive: bool
        player_list_entry: FightResultListEntry.FighterListEntry.PlayerListEntry
        mutant_list_entry: FightResultListEntry.FighterListEntry.MutantListEntry
        tax_collector_list_entry: FightResultListEntry.FighterListEntry.TaxCollectorListEntry
        def __init__(self, fighter_id: _Optional[int] = ..., alive: bool = ..., player_list_entry: _Optional[_Union[FightResultListEntry.FighterListEntry.PlayerListEntry, _Mapping]] = ..., mutant_list_entry: _Optional[_Union[FightResultListEntry.FighterListEntry.MutantListEntry, _Mapping]] = ..., tax_collector_list_entry: _Optional[_Union[FightResultListEntry.FighterListEntry.TaxCollectorListEntry, _Mapping]] = ...) -> None: ...
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    WAVE_FIELD_NUMBER: _ClassVar[int]
    REWARDS_FIELD_NUMBER: _ClassVar[int]
    FIGHTER_LIST_ENTRY_FIELD_NUMBER: _ClassVar[int]
    outcome: FightOutcome
    wave: int
    rewards: FightResultListEntry.FightLoot
    fighter_list_entry: FightResultListEntry.FighterListEntry
    def __init__(self, outcome: _Optional[_Union[FightOutcome, str]] = ..., wave: _Optional[int] = ..., rewards: _Optional[_Union[FightResultListEntry.FightLoot, _Mapping]] = ..., fighter_list_entry: _Optional[_Union[FightResultListEntry.FighterListEntry, _Mapping]] = ...) -> None: ...

class NamedPartyTeamWithOutcome(_message.Message):
    __slots__ = ("team", "outcome")
    TEAM_FIELD_NUMBER: _ClassVar[int]
    OUTCOME_FIELD_NUMBER: _ClassVar[int]
    team: NamedPartyTeam
    outcome: FightOutcome
    def __init__(self, team: _Optional[_Union[NamedPartyTeam, _Mapping]] = ..., outcome: _Optional[_Union[FightOutcome, str]] = ...) -> None: ...

class FightCharacteristics(_message.Message):
    __slots__ = ("characteristics", "summoner", "summoned", "invisibility_state")
    CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    SUMMONER_FIELD_NUMBER: _ClassVar[int]
    SUMMONED_FIELD_NUMBER: _ClassVar[int]
    INVISIBILITY_STATE_FIELD_NUMBER: _ClassVar[int]
    characteristics: _containers.RepeatedCompositeFieldContainer[CharacterCharacteristic]
    summoner: int
    summoned: bool
    invisibility_state: FightInvisibilityState
    def __init__(self, characteristics: _Optional[_Iterable[_Union[CharacterCharacteristic, _Mapping]]] = ..., summoner: _Optional[int] = ..., summoned: bool = ..., invisibility_state: _Optional[_Union[FightInvisibilityState, str]] = ...) -> None: ...

class GuildInformation(_message.Message):
    __slots__ = ("id", "name", "level", "social_information")
    class GuildSocialInformation(_message.Message):
        __slots__ = ("emblem", "detailed_information")
        class GuildDetailedInformation(_message.Message):
            __slots__ = ("leader_id", "members_count", "last_activity_day", "recruitment", "pending_applications_count", "leader_name")
            LEADER_ID_FIELD_NUMBER: _ClassVar[int]
            MEMBERS_COUNT_FIELD_NUMBER: _ClassVar[int]
            LAST_ACTIVITY_DAY_FIELD_NUMBER: _ClassVar[int]
            RECRUITMENT_FIELD_NUMBER: _ClassVar[int]
            PENDING_APPLICATIONS_COUNT_FIELD_NUMBER: _ClassVar[int]
            LEADER_NAME_FIELD_NUMBER: _ClassVar[int]
            leader_id: int
            members_count: int
            last_activity_day: int
            recruitment: GuildRecruitmentInformation
            pending_applications_count: int
            leader_name: str
            def __init__(self, leader_id: _Optional[int] = ..., members_count: _Optional[int] = ..., last_activity_day: _Optional[int] = ..., recruitment: _Optional[_Union[GuildRecruitmentInformation, _Mapping]] = ..., pending_applications_count: _Optional[int] = ..., leader_name: _Optional[str] = ...) -> None: ...
        EMBLEM_FIELD_NUMBER: _ClassVar[int]
        DETAILED_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        emblem: SocialEmblem
        detailed_information: GuildInformation.GuildSocialInformation.GuildDetailedInformation
        def __init__(self, emblem: _Optional[_Union[SocialEmblem, _Mapping]] = ..., detailed_information: _Optional[_Union[GuildInformation.GuildSocialInformation.GuildDetailedInformation, _Mapping]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    SOCIAL_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    level: int
    social_information: GuildInformation.GuildSocialInformation
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., level: _Optional[int] = ..., social_information: _Optional[_Union[GuildInformation.GuildSocialInformation, _Mapping]] = ...) -> None: ...

class GuildRecruitmentInformation(_message.Message):
    __slots__ = ("social_id", "recruitment_type", "title", "text", "selected_languages", "selected_criterion", "min_level", "min_level_facultative", "invalidated_by_moderation", "last_edit_player_name", "last_edit_date", "auto_locked", "min_success", "min_success_facultative")
    SOCIAL_ID_FIELD_NUMBER: _ClassVar[int]
    RECRUITMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SELECTED_LANGUAGES_FIELD_NUMBER: _ClassVar[int]
    SELECTED_CRITERION_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FACULTATIVE_FIELD_NUMBER: _ClassVar[int]
    INVALIDATED_BY_MODERATION_FIELD_NUMBER: _ClassVar[int]
    LAST_EDIT_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_EDIT_DATE_FIELD_NUMBER: _ClassVar[int]
    AUTO_LOCKED_FIELD_NUMBER: _ClassVar[int]
    MIN_SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MIN_SUCCESS_FACULTATIVE_FIELD_NUMBER: _ClassVar[int]
    social_id: int
    recruitment_type: SocialRecruitmentType
    title: str
    text: str
    selected_languages: _containers.RepeatedScalarFieldContainer[int]
    selected_criterion: _containers.RepeatedScalarFieldContainer[int]
    min_level: int
    min_level_facultative: bool
    invalidated_by_moderation: bool
    last_edit_player_name: str
    last_edit_date: int
    auto_locked: bool
    min_success: int
    min_success_facultative: bool
    def __init__(self, social_id: _Optional[int] = ..., recruitment_type: _Optional[_Union[SocialRecruitmentType, str]] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., selected_languages: _Optional[_Iterable[int]] = ..., selected_criterion: _Optional[_Iterable[int]] = ..., min_level: _Optional[int] = ..., min_level_facultative: bool = ..., invalidated_by_moderation: bool = ..., last_edit_player_name: _Optional[str] = ..., last_edit_date: _Optional[int] = ..., auto_locked: bool = ..., min_success: _Optional[int] = ..., min_success_facultative: bool = ...) -> None: ...

class GuildLogbookEntry(_message.Message):
    __slots__ = ("guild_id", "date", "chest_activity", "paddock_activity", "player_flow_activity", "level_up_activity", "Unlock_new_tab_activity", "rank_activity", "player_rank_update_activity")
    class ChestActivity(_message.Message):
        __slots__ = ("player_id", "player_name", "event_type", "quantity", "object", "source_tab_id", "destination_tab_id")
        class ChestEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            DEPOSIT: _ClassVar[GuildLogbookEntry.ChestActivity.ChestEventType]
            WITHDRAW: _ClassVar[GuildLogbookEntry.ChestActivity.ChestEventType]
            TRANSFER: _ClassVar[GuildLogbookEntry.ChestActivity.ChestEventType]
        DEPOSIT: GuildLogbookEntry.ChestActivity.ChestEventType
        WITHDRAW: GuildLogbookEntry.ChestActivity.ChestEventType
        TRANSFER: GuildLogbookEntry.ChestActivity.ChestEventType
        PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
        EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        QUANTITY_FIELD_NUMBER: _ClassVar[int]
        OBJECT_FIELD_NUMBER: _ClassVar[int]
        SOURCE_TAB_ID_FIELD_NUMBER: _ClassVar[int]
        DESTINATION_TAB_ID_FIELD_NUMBER: _ClassVar[int]
        player_id: int
        player_name: str
        event_type: GuildLogbookEntry.ChestActivity.ChestEventType
        quantity: int
        object: ObjectItem
        source_tab_id: int
        destination_tab_id: int
        def __init__(self, player_id: _Optional[int] = ..., player_name: _Optional[str] = ..., event_type: _Optional[_Union[GuildLogbookEntry.ChestActivity.ChestEventType, str]] = ..., quantity: _Optional[int] = ..., object: _Optional[_Union[ObjectItem, _Mapping]] = ..., source_tab_id: _Optional[int] = ..., destination_tab_id: _Optional[int] = ...) -> None: ...
    class PaddockActivity(_message.Message):
        __slots__ = ("player_id", "player_name", "paddock_coordinates", "farm_id", "paddock_commercial_event_type")
        class PaddockCommercialEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            BUY: _ClassVar[GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType]
            PUT_ON_SELL: _ClassVar[GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType]
            SOLD: _ClassVar[GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType]
        BUY: GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType
        PUT_ON_SELL: GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType
        SOLD: GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType
        PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
        PADDOCK_COORDINATES_FIELD_NUMBER: _ClassVar[int]
        FARM_ID_FIELD_NUMBER: _ClassVar[int]
        PADDOCK_COMMERCIAL_EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        player_id: int
        player_name: str
        paddock_coordinates: MapExtendedCoordinates
        farm_id: int
        paddock_commercial_event_type: GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType
        def __init__(self, player_id: _Optional[int] = ..., player_name: _Optional[str] = ..., paddock_coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ..., farm_id: _Optional[int] = ..., paddock_commercial_event_type: _Optional[_Union[GuildLogbookEntry.PaddockActivity.PaddockCommercialEventType, str]] = ...) -> None: ...
    class PlayerFlowActivity(_message.Message):
        __slots__ = ("player_id", "player_name", "player_flow_event_type")
        class PlayerFlowEventType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            JOIN: _ClassVar[GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType]
            LEAVE: _ClassVar[GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType]
            APPLY_REFUSED: _ClassVar[GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType]
        JOIN: GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType
        LEAVE: GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType
        APPLY_REFUSED: GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType
        PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
        PLAYER_FLOW_EVENT_TYPE_FIELD_NUMBER: _ClassVar[int]
        player_id: int
        player_name: str
        player_flow_event_type: GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType
        def __init__(self, player_id: _Optional[int] = ..., player_name: _Optional[str] = ..., player_flow_event_type: _Optional[_Union[GuildLogbookEntry.PlayerFlowActivity.PlayerFlowEventType, str]] = ...) -> None: ...
    class LevelUpActivity(_message.Message):
        __slots__ = ("new_guild_level",)
        NEW_GUILD_LEVEL_FIELD_NUMBER: _ClassVar[int]
        new_guild_level: int
        def __init__(self, new_guild_level: _Optional[int] = ...) -> None: ...
    class UnlockNewTabActivity(_message.Message):
        __slots__ = ()
        def __init__(self) -> None: ...
    class RankActivity(_message.Message):
        __slots__ = ("rank_activity_type", "rank_information")
        class RankActivityType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            CREATION: _ClassVar[GuildLogbookEntry.RankActivity.RankActivityType]
            UPDATE: _ClassVar[GuildLogbookEntry.RankActivity.RankActivityType]
            DELETE: _ClassVar[GuildLogbookEntry.RankActivity.RankActivityType]
        CREATION: GuildLogbookEntry.RankActivity.RankActivityType
        UPDATE: GuildLogbookEntry.RankActivity.RankActivityType
        DELETE: GuildLogbookEntry.RankActivity.RankActivityType
        RANK_ACTIVITY_TYPE_FIELD_NUMBER: _ClassVar[int]
        RANK_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        rank_activity_type: GuildLogbookEntry.RankActivity.RankActivityType
        rank_information: RankInformation
        def __init__(self, rank_activity_type: _Optional[_Union[GuildLogbookEntry.RankActivity.RankActivityType, str]] = ..., rank_information: _Optional[_Union[RankInformation, _Mapping]] = ...) -> None: ...
    class PlayerRankUpdateActivity(_message.Message):
        __slots__ = ("rank_information", "source_player_id", "target_player_id", "source_player_name", "target_player_name")
        RANK_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        SOURCE_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        TARGET_PLAYER_ID_FIELD_NUMBER: _ClassVar[int]
        SOURCE_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
        TARGET_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
        rank_information: RankInformation
        source_player_id: int
        target_player_id: int
        source_player_name: str
        target_player_name: str
        def __init__(self, rank_information: _Optional[_Union[RankInformation, _Mapping]] = ..., source_player_id: _Optional[int] = ..., target_player_id: _Optional[int] = ..., source_player_name: _Optional[str] = ..., target_player_name: _Optional[str] = ...) -> None: ...
    GUILD_ID_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    CHEST_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    PADDOCK_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    PLAYER_FLOW_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    LEVEL_UP_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    UNLOCK_NEW_TAB_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    RANK_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    PLAYER_RANK_UPDATE_ACTIVITY_FIELD_NUMBER: _ClassVar[int]
    guild_id: int
    date: int
    chest_activity: GuildLogbookEntry.ChestActivity
    paddock_activity: GuildLogbookEntry.PaddockActivity
    player_flow_activity: GuildLogbookEntry.PlayerFlowActivity
    level_up_activity: GuildLogbookEntry.LevelUpActivity
    Unlock_new_tab_activity: GuildLogbookEntry.UnlockNewTabActivity
    rank_activity: GuildLogbookEntry.RankActivity
    player_rank_update_activity: GuildLogbookEntry.PlayerRankUpdateActivity
    def __init__(self, guild_id: _Optional[int] = ..., date: _Optional[int] = ..., chest_activity: _Optional[_Union[GuildLogbookEntry.ChestActivity, _Mapping]] = ..., paddock_activity: _Optional[_Union[GuildLogbookEntry.PaddockActivity, _Mapping]] = ..., player_flow_activity: _Optional[_Union[GuildLogbookEntry.PlayerFlowActivity, _Mapping]] = ..., level_up_activity: _Optional[_Union[GuildLogbookEntry.LevelUpActivity, _Mapping]] = ..., Unlock_new_tab_activity: _Optional[_Union[GuildLogbookEntry.UnlockNewTabActivity, _Mapping]] = ..., rank_activity: _Optional[_Union[GuildLogbookEntry.RankActivity, _Mapping]] = ..., player_rank_update_activity: _Optional[_Union[GuildLogbookEntry.PlayerRankUpdateActivity, _Mapping]] = ...) -> None: ...

class HouseInstance(_message.Message):
    __slots__ = ("instance_id", "second_hand", "is_locked", "account_tag", "has_owner", "price", "is_sale_locked", "is_admin_locked", "guild_information", "rooms_count", "chests_count", "skills_id")
    INSTANCE_ID_FIELD_NUMBER: _ClassVar[int]
    SECOND_HAND_FIELD_NUMBER: _ClassVar[int]
    IS_LOCKED_FIELD_NUMBER: _ClassVar[int]
    ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    HAS_OWNER_FIELD_NUMBER: _ClassVar[int]
    PRICE_FIELD_NUMBER: _ClassVar[int]
    IS_SALE_LOCKED_FIELD_NUMBER: _ClassVar[int]
    IS_ADMIN_LOCKED_FIELD_NUMBER: _ClassVar[int]
    GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    ROOMS_COUNT_FIELD_NUMBER: _ClassVar[int]
    CHESTS_COUNT_FIELD_NUMBER: _ClassVar[int]
    SKILLS_ID_FIELD_NUMBER: _ClassVar[int]
    instance_id: int
    second_hand: bool
    is_locked: bool
    account_tag: AccountTag
    has_owner: bool
    price: int
    is_sale_locked: bool
    is_admin_locked: bool
    guild_information: GuildInformation
    rooms_count: int
    chests_count: int
    skills_id: _containers.RepeatedScalarFieldContainer[int]
    def __init__(self, instance_id: _Optional[int] = ..., second_hand: bool = ..., is_locked: bool = ..., account_tag: _Optional[_Union[AccountTag, _Mapping]] = ..., has_owner: bool = ..., price: _Optional[int] = ..., is_sale_locked: bool = ..., is_admin_locked: bool = ..., guild_information: _Optional[_Union[GuildInformation, _Mapping]] = ..., rooms_count: _Optional[int] = ..., chests_count: _Optional[int] = ..., skills_id: _Optional[_Iterable[int]] = ...) -> None: ...

class House(_message.Message):
    __slots__ = ("house_id", "model_id", "house_account", "house_on_map", "house_inside", "house_guild")
    class HouseAccount(_message.Message):
        __slots__ = ("house_information", "coordinates")
        HOUSE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        house_information: HouseInstance
        coordinates: MapExtendedCoordinates
        def __init__(self, house_information: _Optional[_Union[HouseInstance, _Mapping]] = ..., coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ...) -> None: ...
    class HouseOnMap(_message.Message):
        __slots__ = ("doors_on_map", "houses_information")
        DOORS_ON_MAP_FIELD_NUMBER: _ClassVar[int]
        HOUSES_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        doors_on_map: _containers.RepeatedScalarFieldContainer[int]
        houses_information: _containers.RepeatedCompositeFieldContainer[HouseInstance]
        def __init__(self, doors_on_map: _Optional[_Iterable[int]] = ..., houses_information: _Optional[_Iterable[_Union[HouseInstance, _Mapping]]] = ...) -> None: ...
    class HouseInside(_message.Message):
        __slots__ = ("house_information", "coordinates")
        HOUSE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        house_information: HouseInstance
        coordinates: MapCoordinates
        def __init__(self, house_information: _Optional[_Union[HouseInstance, _Mapping]] = ..., coordinates: _Optional[_Union[MapCoordinates, _Mapping]] = ...) -> None: ...
    class HouseGuild(_message.Message):
        __slots__ = ("house_information", "coordinates", "skills_id", "guild_share_params")
        HOUSE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        SKILLS_ID_FIELD_NUMBER: _ClassVar[int]
        GUILD_SHARE_PARAMS_FIELD_NUMBER: _ClassVar[int]
        house_information: HouseInstance
        coordinates: MapExtendedCoordinates
        skills_id: _containers.RepeatedScalarFieldContainer[int]
        guild_share_params: int
        def __init__(self, house_information: _Optional[_Union[HouseInstance, _Mapping]] = ..., coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ..., skills_id: _Optional[_Iterable[int]] = ..., guild_share_params: _Optional[int] = ...) -> None: ...
    HOUSE_ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    HOUSE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    HOUSE_ON_MAP_FIELD_NUMBER: _ClassVar[int]
    HOUSE_INSIDE_FIELD_NUMBER: _ClassVar[int]
    HOUSE_GUILD_FIELD_NUMBER: _ClassVar[int]
    house_id: int
    model_id: int
    house_account: House.HouseAccount
    house_on_map: House.HouseOnMap
    house_inside: House.HouseInside
    house_guild: House.HouseGuild
    def __init__(self, house_id: _Optional[int] = ..., model_id: _Optional[int] = ..., house_account: _Optional[_Union[House.HouseAccount, _Mapping]] = ..., house_on_map: _Optional[_Union[House.HouseOnMap, _Mapping]] = ..., house_inside: _Optional[_Union[House.HouseInside, _Mapping]] = ..., house_guild: _Optional[_Union[House.HouseGuild, _Mapping]] = ...) -> None: ...

class Shortcut(_message.Message):
    __slots__ = ("slot_id", "shortcut_object_item", "shortcut_preset", "shortcut_spell", "shortcut_smiley", "shortcut_emote", "shortcut_cosmetic_object", "shortcut_outfit")
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_OBJECT_ITEM_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_PRESET_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_SPELL_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_SMILEY_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_EMOTE_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_COSMETIC_OBJECT_FIELD_NUMBER: _ClassVar[int]
    SHORTCUT_OUTFIT_FIELD_NUMBER: _ClassVar[int]
    slot_id: int
    shortcut_object_item: ShortcutObjectItem
    shortcut_preset: ShortcutPreset
    shortcut_spell: ShortcutSpell
    shortcut_smiley: ShortcutSmiley
    shortcut_emote: ShortcutEmote
    shortcut_cosmetic_object: ShortcutCosmeticObject
    shortcut_outfit: ShortcutOutfit
    def __init__(self, slot_id: _Optional[int] = ..., shortcut_object_item: _Optional[_Union[ShortcutObjectItem, _Mapping]] = ..., shortcut_preset: _Optional[_Union[ShortcutPreset, _Mapping]] = ..., shortcut_spell: _Optional[_Union[ShortcutSpell, _Mapping]] = ..., shortcut_smiley: _Optional[_Union[ShortcutSmiley, _Mapping]] = ..., shortcut_emote: _Optional[_Union[ShortcutEmote, _Mapping]] = ..., shortcut_cosmetic_object: _Optional[_Union[ShortcutCosmeticObject, _Mapping]] = ..., shortcut_outfit: _Optional[_Union[ShortcutOutfit, _Mapping]] = ...) -> None: ...

class ShortcutObjectItem(_message.Message):
    __slots__ = ("item_uid", "item_gid")
    ITEM_UID_FIELD_NUMBER: _ClassVar[int]
    ITEM_GID_FIELD_NUMBER: _ClassVar[int]
    item_uid: int
    item_gid: int
    def __init__(self, item_uid: _Optional[int] = ..., item_gid: _Optional[int] = ...) -> None: ...

class ShortcutSpell(_message.Message):
    __slots__ = ("spell_id",)
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    def __init__(self, spell_id: _Optional[int] = ...) -> None: ...

class ShortcutSmiley(_message.Message):
    __slots__ = ("smiley_id",)
    SMILEY_ID_FIELD_NUMBER: _ClassVar[int]
    smiley_id: int
    def __init__(self, smiley_id: _Optional[int] = ...) -> None: ...

class ShortcutEmote(_message.Message):
    __slots__ = ("emote_id",)
    EMOTE_ID_FIELD_NUMBER: _ClassVar[int]
    emote_id: int
    def __init__(self, emote_id: _Optional[int] = ...) -> None: ...

class ShortcutCosmeticObject(_message.Message):
    __slots__ = ("object_gid", "skin_id", "enable")
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    SKIN_ID_FIELD_NUMBER: _ClassVar[int]
    ENABLE_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    skin_id: int
    enable: bool
    def __init__(self, object_gid: _Optional[int] = ..., skin_id: _Optional[int] = ..., enable: bool = ...) -> None: ...

class ShortcutOutfit(_message.Message):
    __slots__ = ("outfit_uuid",)
    OUTFIT_UUID_FIELD_NUMBER: _ClassVar[int]
    outfit_uuid: str
    def __init__(self, outfit_uuid: _Optional[str] = ...) -> None: ...

class ShortcutPreset(_message.Message):
    __slots__ = ("preset_uuid", "type")
    PRESET_UUID_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    preset_uuid: str
    type: PresetType
    def __init__(self, preset_uuid: _Optional[str] = ..., type: _Optional[_Union[PresetType, str]] = ...) -> None: ...

class MapCoordinates(_message.Message):
    __slots__ = ("world_x", "world_y")
    WORLD_X_FIELD_NUMBER: _ClassVar[int]
    WORLD_Y_FIELD_NUMBER: _ClassVar[int]
    world_x: int
    world_y: int
    def __init__(self, world_x: _Optional[int] = ..., world_y: _Optional[int] = ...) -> None: ...

class MapExtendedCoordinates(_message.Message):
    __slots__ = ("world_x", "world_y", "map_id", "sub_area_id")
    WORLD_X_FIELD_NUMBER: _ClassVar[int]
    WORLD_Y_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
    world_x: int
    world_y: int
    map_id: int
    sub_area_id: int
    def __init__(self, world_x: _Optional[int] = ..., world_y: _Optional[int] = ..., map_id: _Optional[int] = ..., sub_area_id: _Optional[int] = ...) -> None: ...

class MonsterGroupStaticInformation(_message.Message):
    __slots__ = ("main_creature", "underlings", "alternatives")
    MAIN_CREATURE_FIELD_NUMBER: _ClassVar[int]
    UNDERLINGS_FIELD_NUMBER: _ClassVar[int]
    ALTERNATIVES_FIELD_NUMBER: _ClassVar[int]
    main_creature: MonsterInGroupInformation
    underlings: _containers.RepeatedCompositeFieldContainer[MonsterInGroupInformation]
    alternatives: _containers.RepeatedCompositeFieldContainer[MonstersInGroupAlternativeInformation]
    def __init__(self, main_creature: _Optional[_Union[MonsterInGroupInformation, _Mapping]] = ..., underlings: _Optional[_Iterable[_Union[MonsterInGroupInformation, _Mapping]]] = ..., alternatives: _Optional[_Iterable[_Union[MonstersInGroupAlternativeInformation, _Mapping]]] = ...) -> None: ...

class MonsterInGroupInformation(_message.Message):
    __slots__ = ("gid", "grade", "level", "look")
    GID_FIELD_NUMBER: _ClassVar[int]
    GRADE_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    LOOK_FIELD_NUMBER: _ClassVar[int]
    gid: int
    grade: int
    level: int
    look: EntityLook
    def __init__(self, gid: _Optional[int] = ..., grade: _Optional[int] = ..., level: _Optional[int] = ..., look: _Optional[_Union[EntityLook, _Mapping]] = ...) -> None: ...

class MonstersInGroupAlternativeInformation(_message.Message):
    __slots__ = ("player_count", "monsters")
    PLAYER_COUNT_FIELD_NUMBER: _ClassVar[int]
    MONSTERS_FIELD_NUMBER: _ClassVar[int]
    player_count: int
    monsters: _containers.RepeatedCompositeFieldContainer[MonsterInGroupInformation]
    def __init__(self, player_count: _Optional[int] = ..., monsters: _Optional[_Iterable[_Union[MonsterInGroupInformation, _Mapping]]] = ...) -> None: ...

class ItemMinimalInformation(_message.Message):
    __slots__ = ("object_gid", "effects", "quantity", "item_to_sell_in_npc_shop")
    class ItemToSellInNpcShop(_message.Message):
        __slots__ = ("price", "buy_criterion")
        PRICE_FIELD_NUMBER: _ClassVar[int]
        BUY_CRITERION_FIELD_NUMBER: _ClassVar[int]
        price: int
        buy_criterion: str
        def __init__(self, price: _Optional[int] = ..., buy_criterion: _Optional[str] = ...) -> None: ...
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    ITEM_TO_SELL_IN_NPC_SHOP_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    effects: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
    quantity: int
    item_to_sell_in_npc_shop: ItemMinimalInformation.ItemToSellInNpcShop
    def __init__(self, object_gid: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ..., quantity: _Optional[int] = ..., item_to_sell_in_npc_shop: _Optional[_Union[ItemMinimalInformation.ItemToSellInNpcShop, _Mapping]] = ...) -> None: ...

class ObjectGidWithQuantity(_message.Message):
    __slots__ = ("object_gid", "quantity", "price_date_effect")
    class ObjectPriceDateEffect(_message.Message):
        __slots__ = ("price", "effects", "date")
        PRICE_FIELD_NUMBER: _ClassVar[int]
        EFFECTS_FIELD_NUMBER: _ClassVar[int]
        DATE_FIELD_NUMBER: _ClassVar[int]
        price: int
        effects: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
        date: int
        def __init__(self, price: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ..., date: _Optional[int] = ...) -> None: ...
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    PRICE_DATE_EFFECT_FIELD_NUMBER: _ClassVar[int]
    object_gid: int
    quantity: int
    price_date_effect: ObjectGidWithQuantity.ObjectPriceDateEffect
    def __init__(self, object_gid: _Optional[int] = ..., quantity: _Optional[int] = ..., price_date_effect: _Optional[_Union[ObjectGidWithQuantity.ObjectPriceDateEffect, _Mapping]] = ...) -> None: ...

class ObjectUidWithQuantity(_message.Message):
    __slots__ = ("object_uid", "quantity")
    OBJECT_UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    object_uid: int
    quantity: int
    def __init__(self, object_uid: _Optional[int] = ..., quantity: _Optional[int] = ...) -> None: ...

class ObjectItemInventory(_message.Message):
    __slots__ = ("position", "item", "favorite", "tag_storage_uuids")
    POSITION_FIELD_NUMBER: _ClassVar[int]
    ITEM_FIELD_NUMBER: _ClassVar[int]
    FAVORITE_FIELD_NUMBER: _ClassVar[int]
    TAG_STORAGE_UUIDS_FIELD_NUMBER: _ClassVar[int]
    position: int
    item: ObjectItem
    favorite: bool
    tag_storage_uuids: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, position: _Optional[int] = ..., item: _Optional[_Union[ObjectItem, _Mapping]] = ..., favorite: bool = ..., tag_storage_uuids: _Optional[_Iterable[str]] = ...) -> None: ...

class ObjectItem(_message.Message):
    __slots__ = ("uid", "quantity", "gid", "effects")
    UID_FIELD_NUMBER: _ClassVar[int]
    QUANTITY_FIELD_NUMBER: _ClassVar[int]
    GID_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    uid: int
    quantity: int
    gid: int
    effects: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
    def __init__(self, uid: _Optional[int] = ..., quantity: _Optional[int] = ..., gid: _Optional[int] = ..., effects: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ...) -> None: ...

class ObjectEffect(_message.Message):
    __slots__ = ("action", "value_string", "value_int", "min_max", "dice", "date", "duration_minute", "creature_family", "monster_count", "mount")
    class DofusDate(_message.Message):
        __slots__ = ("year", "month", "day", "hour", "minute")
        YEAR_FIELD_NUMBER: _ClassVar[int]
        MONTH_FIELD_NUMBER: _ClassVar[int]
        DAY_FIELD_NUMBER: _ClassVar[int]
        HOUR_FIELD_NUMBER: _ClassVar[int]
        MINUTE_FIELD_NUMBER: _ClassVar[int]
        year: int
        month: int
        day: int
        hour: int
        minute: int
        def __init__(self, year: _Optional[int] = ..., month: _Optional[int] = ..., day: _Optional[int] = ..., hour: _Optional[int] = ..., minute: _Optional[int] = ...) -> None: ...
    class ObjectEffectMinMaxValue(_message.Message):
        __slots__ = ("min", "max")
        MIN_FIELD_NUMBER: _ClassVar[int]
        MAX_FIELD_NUMBER: _ClassVar[int]
        min: int
        max: int
        def __init__(self, min: _Optional[int] = ..., max: _Optional[int] = ...) -> None: ...
    class ObjectEffectDiceValue(_message.Message):
        __slots__ = ("num", "side", "const")
        NUM_FIELD_NUMBER: _ClassVar[int]
        SIDE_FIELD_NUMBER: _ClassVar[int]
        CONST_FIELD_NUMBER: _ClassVar[int]
        num: int
        side: int
        const: int
        def __init__(self, num: _Optional[int] = ..., side: _Optional[int] = ..., const: _Optional[int] = ...) -> None: ...
    class MonsterCount(_message.Message):
        __slots__ = ("creature_family", "count")
        CREATURE_FAMILY_FIELD_NUMBER: _ClassVar[int]
        COUNT_FIELD_NUMBER: _ClassVar[int]
        creature_family: int
        count: int
        def __init__(self, creature_family: _Optional[int] = ..., count: _Optional[int] = ...) -> None: ...
    class ObjectEffectMountValue(_message.Message):
        __slots__ = ("certificate_id", "date_expiration", "model_id", "mount_name", "owner_name", "mount_level", "mount_gender", "rideable", "impregnated", "impregnate_ready", "reproduction_count", "reproduction_max", "effect", "capacity")
        CERTIFICATE_ID_FIELD_NUMBER: _ClassVar[int]
        DATE_EXPIRATION_FIELD_NUMBER: _ClassVar[int]
        MODEL_ID_FIELD_NUMBER: _ClassVar[int]
        MOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
        OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
        MOUNT_LEVEL_FIELD_NUMBER: _ClassVar[int]
        MOUNT_GENDER_FIELD_NUMBER: _ClassVar[int]
        RIDEABLE_FIELD_NUMBER: _ClassVar[int]
        IMPREGNATED_FIELD_NUMBER: _ClassVar[int]
        IMPREGNATE_READY_FIELD_NUMBER: _ClassVar[int]
        REPRODUCTION_COUNT_FIELD_NUMBER: _ClassVar[int]
        REPRODUCTION_MAX_FIELD_NUMBER: _ClassVar[int]
        EFFECT_FIELD_NUMBER: _ClassVar[int]
        CAPACITY_FIELD_NUMBER: _ClassVar[int]
        certificate_id: int
        date_expiration: str
        model_id: int
        mount_name: str
        owner_name: str
        mount_level: int
        mount_gender: Gender
        rideable: bool
        impregnated: bool
        impregnate_ready: bool
        reproduction_count: int
        reproduction_max: int
        effect: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
        capacity: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, certificate_id: _Optional[int] = ..., date_expiration: _Optional[str] = ..., model_id: _Optional[int] = ..., mount_name: _Optional[str] = ..., owner_name: _Optional[str] = ..., mount_level: _Optional[int] = ..., mount_gender: _Optional[_Union[Gender, str]] = ..., rideable: bool = ..., impregnated: bool = ..., impregnate_ready: bool = ..., reproduction_count: _Optional[int] = ..., reproduction_max: _Optional[int] = ..., effect: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ..., capacity: _Optional[_Iterable[int]] = ...) -> None: ...
    ACTION_FIELD_NUMBER: _ClassVar[int]
    VALUE_STRING_FIELD_NUMBER: _ClassVar[int]
    VALUE_INT_FIELD_NUMBER: _ClassVar[int]
    MIN_MAX_FIELD_NUMBER: _ClassVar[int]
    DICE_FIELD_NUMBER: _ClassVar[int]
    DATE_FIELD_NUMBER: _ClassVar[int]
    DURATION_MINUTE_FIELD_NUMBER: _ClassVar[int]
    CREATURE_FAMILY_FIELD_NUMBER: _ClassVar[int]
    MONSTER_COUNT_FIELD_NUMBER: _ClassVar[int]
    MOUNT_FIELD_NUMBER: _ClassVar[int]
    action: int
    value_string: str
    value_int: int
    min_max: ObjectEffect.ObjectEffectMinMaxValue
    dice: ObjectEffect.ObjectEffectDiceValue
    date: ObjectEffect.DofusDate
    duration_minute: int
    creature_family: int
    monster_count: ObjectEffect.MonsterCount
    mount: ObjectEffect.ObjectEffectMountValue
    def __init__(self, action: _Optional[int] = ..., value_string: _Optional[str] = ..., value_int: _Optional[int] = ..., min_max: _Optional[_Union[ObjectEffect.ObjectEffectMinMaxValue, _Mapping]] = ..., dice: _Optional[_Union[ObjectEffect.ObjectEffectDiceValue, _Mapping]] = ..., date: _Optional[_Union[ObjectEffect.DofusDate, _Mapping]] = ..., duration_minute: _Optional[int] = ..., creature_family: _Optional[int] = ..., monster_count: _Optional[_Union[ObjectEffect.MonsterCount, _Mapping]] = ..., mount: _Optional[_Union[ObjectEffect.ObjectEffectMountValue, _Mapping]] = ...) -> None: ...

class ObjectInRolePlay(_message.Message):
    __slots__ = ("cell_id", "object_gid", "with_look", "paddock_item")
    class WithLook(_message.Message):
        __slots__ = ("look", "direction")
        LOOK_FIELD_NUMBER: _ClassVar[int]
        DIRECTION_FIELD_NUMBER: _ClassVar[int]
        look: EntityLook
        direction: Direction
        def __init__(self, look: _Optional[_Union[EntityLook, _Mapping]] = ..., direction: _Optional[_Union[Direction, str]] = ...) -> None: ...
    class PaddockItem(_message.Message):
        __slots__ = ("durability", "durability_max")
        DURABILITY_FIELD_NUMBER: _ClassVar[int]
        DURABILITY_MAX_FIELD_NUMBER: _ClassVar[int]
        durability: int
        durability_max: int
        def __init__(self, durability: _Optional[int] = ..., durability_max: _Optional[int] = ...) -> None: ...
    CELL_ID_FIELD_NUMBER: _ClassVar[int]
    OBJECT_GID_FIELD_NUMBER: _ClassVar[int]
    WITH_LOOK_FIELD_NUMBER: _ClassVar[int]
    PADDOCK_ITEM_FIELD_NUMBER: _ClassVar[int]
    cell_id: int
    object_gid: int
    with_look: ObjectInRolePlay.WithLook
    paddock_item: ObjectInRolePlay.PaddockItem
    def __init__(self, cell_id: _Optional[int] = ..., object_gid: _Optional[int] = ..., with_look: _Optional[_Union[ObjectInRolePlay.WithLook, _Mapping]] = ..., paddock_item: _Optional[_Union[ObjectInRolePlay.PaddockItem, _Mapping]] = ...) -> None: ...

class GameActionItem(_message.Message):
    __slots__ = ("id", "title", "text", "desc_url", "picture_url", "items")
    ID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    DESC_URL_FIELD_NUMBER: _ClassVar[int]
    PICTURE_URL_FIELD_NUMBER: _ClassVar[int]
    ITEMS_FIELD_NUMBER: _ClassVar[int]
    id: int
    title: str
    text: str
    desc_url: str
    picture_url: str
    items: _containers.RepeatedCompositeFieldContainer[ItemMinimalInformation]
    def __init__(self, id: _Optional[int] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., desc_url: _Optional[str] = ..., picture_url: _Optional[str] = ..., items: _Optional[_Iterable[_Union[ItemMinimalInformation, _Mapping]]] = ...) -> None: ...

class PortalInformation(_message.Message):
    __slots__ = ("portal_id", "area_id")
    PORTAL_ID_FIELD_NUMBER: _ClassVar[int]
    AREA_ID_FIELD_NUMBER: _ClassVar[int]
    portal_id: int
    area_id: int
    def __init__(self, portal_id: _Optional[int] = ..., area_id: _Optional[int] = ...) -> None: ...

class PrismInformation(_message.Message):
    __slots__ = ("state", "placement_date", "nuggets_count", "durability", "next_evolution_date", "alliance_information", "module", "cristal", "cristal_number_left")
    class PrismState(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NORMAL: _ClassVar[PrismInformation.PrismState]
        WEAKENED: _ClassVar[PrismInformation.PrismState]
        VULNERABLE: _ClassVar[PrismInformation.PrismState]
        PROTECTED: _ClassVar[PrismInformation.PrismState]
        INHIBITED: _ClassVar[PrismInformation.PrismState]
    NORMAL: PrismInformation.PrismState
    WEAKENED: PrismInformation.PrismState
    VULNERABLE: PrismInformation.PrismState
    PROTECTED: PrismInformation.PrismState
    INHIBITED: PrismInformation.PrismState
    STATE_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_DATE_FIELD_NUMBER: _ClassVar[int]
    NUGGETS_COUNT_FIELD_NUMBER: _ClassVar[int]
    DURABILITY_FIELD_NUMBER: _ClassVar[int]
    NEXT_EVOLUTION_DATE_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    MODULE_FIELD_NUMBER: _ClassVar[int]
    CRISTAL_FIELD_NUMBER: _ClassVar[int]
    CRISTAL_NUMBER_LEFT_FIELD_NUMBER: _ClassVar[int]
    state: PrismInformation.PrismState
    placement_date: int
    nuggets_count: int
    durability: int
    next_evolution_date: int
    alliance_information: AllianceInformation
    module: PrismModule
    cristal: PrismCristal
    cristal_number_left: int
    def __init__(self, state: _Optional[_Union[PrismInformation.PrismState, str]] = ..., placement_date: _Optional[int] = ..., nuggets_count: _Optional[int] = ..., durability: _Optional[int] = ..., next_evolution_date: _Optional[int] = ..., alliance_information: _Optional[_Union[AllianceInformation, _Mapping]] = ..., module: _Optional[_Union[PrismModule, _Mapping]] = ..., cristal: _Optional[_Union[PrismCristal, _Mapping]] = ..., cristal_number_left: _Optional[int] = ...) -> None: ...

class PrismLocalizedInformation(_message.Message):
    __slots__ = ("sub_area_id", "alliance_uid", "map_coordinates", "map_id", "prism")
    SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_UID_FIELD_NUMBER: _ClassVar[int]
    MAP_COORDINATES_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    PRISM_FIELD_NUMBER: _ClassVar[int]
    sub_area_id: int
    alliance_uid: str
    map_coordinates: MapCoordinates
    map_id: int
    prism: PrismInformation
    def __init__(self, sub_area_id: _Optional[int] = ..., alliance_uid: _Optional[str] = ..., map_coordinates: _Optional[_Union[MapCoordinates, _Mapping]] = ..., map_id: _Optional[int] = ..., prism: _Optional[_Union[PrismInformation, _Mapping]] = ...) -> None: ...

class PrismModule(_message.Message):
    __slots__ = ("module_object", "type")
    class PrismModuleType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NO_MODULE: _ClassVar[PrismModule.PrismModuleType]
        TELEPORTER: _ClassVar[PrismModule.PrismModuleType]
        RECYCLER: _ClassVar[PrismModule.PrismModuleType]
    NO_MODULE: PrismModule.PrismModuleType
    TELEPORTER: PrismModule.PrismModuleType
    RECYCLER: PrismModule.PrismModuleType
    MODULE_OBJECT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    module_object: ObjectItemInventory
    type: PrismModule.PrismModuleType
    def __init__(self, module_object: _Optional[_Union[ObjectItemInventory, _Mapping]] = ..., type: _Optional[_Union[PrismModule.PrismModuleType, str]] = ...) -> None: ...

class PrismCristal(_message.Message):
    __slots__ = ("cristal_object", "type")
    class PrismCristalType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        NO_CRISTAL: _ClassVar[PrismCristal.PrismCristalType]
        PROTECTIVE: _ClassVar[PrismCristal.PrismCristalType]
        INHIBITOR: _ClassVar[PrismCristal.PrismCristalType]
    NO_CRISTAL: PrismCristal.PrismCristalType
    PROTECTIVE: PrismCristal.PrismCristalType
    INHIBITOR: PrismCristal.PrismCristalType
    CRISTAL_OBJECT_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    cristal_object: ObjectItemInventory
    type: PrismCristal.PrismCristalType
    def __init__(self, cristal_object: _Optional[_Union[ObjectItemInventory, _Mapping]] = ..., type: _Optional[_Union[PrismCristal.PrismCristalType, str]] = ...) -> None: ...

class AllianceRecruitmentInformation(_message.Message):
    __slots__ = ("social_uid", "recruitment_type", "title", "text", "selected_languages", "selected_criterion", "min_level", "min_level_facultative", "invalidated_by_moderation", "last_edit_player_name", "last_edit_date", "auto_locked")
    SOCIAL_UID_FIELD_NUMBER: _ClassVar[int]
    RECRUITMENT_TYPE_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    SELECTED_LANGUAGES_FIELD_NUMBER: _ClassVar[int]
    SELECTED_CRITERION_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FIELD_NUMBER: _ClassVar[int]
    MIN_LEVEL_FACULTATIVE_FIELD_NUMBER: _ClassVar[int]
    INVALIDATED_BY_MODERATION_FIELD_NUMBER: _ClassVar[int]
    LAST_EDIT_PLAYER_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_EDIT_DATE_FIELD_NUMBER: _ClassVar[int]
    AUTO_LOCKED_FIELD_NUMBER: _ClassVar[int]
    social_uid: str
    recruitment_type: SocialRecruitmentType
    title: str
    text: str
    selected_languages: _containers.RepeatedScalarFieldContainer[int]
    selected_criterion: _containers.RepeatedScalarFieldContainer[int]
    min_level: int
    min_level_facultative: bool
    invalidated_by_moderation: bool
    last_edit_player_name: str
    last_edit_date: int
    auto_locked: bool
    def __init__(self, social_uid: _Optional[str] = ..., recruitment_type: _Optional[_Union[SocialRecruitmentType, str]] = ..., title: _Optional[str] = ..., text: _Optional[str] = ..., selected_languages: _Optional[_Iterable[int]] = ..., selected_criterion: _Optional[_Iterable[int]] = ..., min_level: _Optional[int] = ..., min_level_facultative: bool = ..., invalidated_by_moderation: bool = ..., last_edit_player_name: _Optional[str] = ..., last_edit_date: _Optional[int] = ..., auto_locked: bool = ...) -> None: ...

class SocialEmblem(_message.Message):
    __slots__ = ("symbol_shape_id", "symbol_color", "background_shape_id", "background_color")
    SYMBOL_SHAPE_ID_FIELD_NUMBER: _ClassVar[int]
    SYMBOL_COLOR_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_SHAPE_ID_FIELD_NUMBER: _ClassVar[int]
    BACKGROUND_COLOR_FIELD_NUMBER: _ClassVar[int]
    symbol_shape_id: int
    symbol_color: int
    background_shape_id: int
    background_color: int
    def __init__(self, symbol_shape_id: _Optional[int] = ..., symbol_color: _Optional[int] = ..., background_shape_id: _Optional[int] = ..., background_color: _Optional[int] = ...) -> None: ...

class SocialNoticeInformation(_message.Message):
    __slots__ = ("content", "timestamp", "member_id", "member_name")
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    TIMESTAMP_FIELD_NUMBER: _ClassVar[int]
    MEMBER_ID_FIELD_NUMBER: _ClassVar[int]
    MEMBER_NAME_FIELD_NUMBER: _ClassVar[int]
    content: str
    timestamp: int
    member_id: int
    member_name: str
    def __init__(self, content: _Optional[str] = ..., timestamp: _Optional[int] = ..., member_id: _Optional[int] = ..., member_name: _Optional[str] = ...) -> None: ...

class RankInformation(_message.Message):
    __slots__ = ("id", "name", "order_and_gfx", "private_information")
    class OrderAndGfx(_message.Message):
        __slots__ = ("order", "gfx_id")
        ORDER_FIELD_NUMBER: _ClassVar[int]
        GFX_ID_FIELD_NUMBER: _ClassVar[int]
        order: int
        gfx_id: int
        def __init__(self, order: _Optional[int] = ..., gfx_id: _Optional[int] = ...) -> None: ...
    class PrivateInformation(_message.Message):
        __slots__ = ("modifiable", "rights")
        MODIFIABLE_FIELD_NUMBER: _ClassVar[int]
        RIGHTS_FIELD_NUMBER: _ClassVar[int]
        modifiable: bool
        rights: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, modifiable: bool = ..., rights: _Optional[_Iterable[int]] = ...) -> None: ...
    ID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    ORDER_AND_GFX_FIELD_NUMBER: _ClassVar[int]
    PRIVATE_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    id: int
    name: str
    order_and_gfx: RankInformation.OrderAndGfx
    private_information: RankInformation.PrivateInformation
    def __init__(self, id: _Optional[int] = ..., name: _Optional[str] = ..., order_and_gfx: _Optional[_Union[RankInformation.OrderAndGfx, _Mapping]] = ..., private_information: _Optional[_Union[RankInformation.PrivateInformation, _Mapping]] = ...) -> None: ...

class TaxCollectorInformation(_message.Message):
    __slots__ = ("uid", "first_name_id", "last_name_id", "alliance", "caller_id", "caller_name", "hired_date", "coordinates", "sub_area_id", "map_id", "state", "entity_look", "complementary_information", "character_characteristics", "equipments", "spells")
    UID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_FIELD_NUMBER: _ClassVar[int]
    CALLER_ID_FIELD_NUMBER: _ClassVar[int]
    CALLER_NAME_FIELD_NUMBER: _ClassVar[int]
    HIRED_DATE_FIELD_NUMBER: _ClassVar[int]
    COORDINATES_FIELD_NUMBER: _ClassVar[int]
    SUB_AREA_ID_FIELD_NUMBER: _ClassVar[int]
    MAP_ID_FIELD_NUMBER: _ClassVar[int]
    STATE_FIELD_NUMBER: _ClassVar[int]
    ENTITY_LOOK_FIELD_NUMBER: _ClassVar[int]
    COMPLEMENTARY_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    CHARACTER_CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENTS_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    uid: str
    first_name_id: int
    last_name_id: int
    alliance: AllianceInformation
    caller_id: int
    caller_name: str
    hired_date: int
    coordinates: MapCoordinates
    sub_area_id: int
    map_id: int
    state: TaxCollectorState
    entity_look: EntityLook
    complementary_information: _containers.RepeatedCompositeFieldContainer[TaxCollectorComplementaryInformation]
    character_characteristics: _containers.RepeatedCompositeFieldContainer[CharacterCharacteristic]
    equipments: _containers.RepeatedCompositeFieldContainer[ObjectItemInventory]
    spells: _containers.RepeatedCompositeFieldContainer[TaxCollectorOrderedSpell]
    def __init__(self, uid: _Optional[str] = ..., first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., alliance: _Optional[_Union[AllianceInformation, _Mapping]] = ..., caller_id: _Optional[int] = ..., caller_name: _Optional[str] = ..., hired_date: _Optional[int] = ..., coordinates: _Optional[_Union[MapCoordinates, _Mapping]] = ..., sub_area_id: _Optional[int] = ..., map_id: _Optional[int] = ..., state: _Optional[_Union[TaxCollectorState, str]] = ..., entity_look: _Optional[_Union[EntityLook, _Mapping]] = ..., complementary_information: _Optional[_Iterable[_Union[TaxCollectorComplementaryInformation, _Mapping]]] = ..., character_characteristics: _Optional[_Iterable[_Union[CharacterCharacteristic, _Mapping]]] = ..., equipments: _Optional[_Iterable[_Union[ObjectItemInventory, _Mapping]]] = ..., spells: _Optional[_Iterable[_Union[TaxCollectorOrderedSpell, _Mapping]]] = ...) -> None: ...

class TaxCollectorStaticInformation(_message.Message):
    __slots__ = ("uid", "first_name_id", "last_name_id", "alliance", "caller_id")
    UID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_ID_FIELD_NUMBER: _ClassVar[int]
    ALLIANCE_FIELD_NUMBER: _ClassVar[int]
    CALLER_ID_FIELD_NUMBER: _ClassVar[int]
    uid: str
    first_name_id: int
    last_name_id: int
    alliance: AllianceInformation
    caller_id: int
    def __init__(self, uid: _Optional[str] = ..., first_name_id: _Optional[int] = ..., last_name_id: _Optional[int] = ..., alliance: _Optional[_Union[AllianceInformation, _Mapping]] = ..., caller_id: _Optional[int] = ...) -> None: ...

class TaxCollectorComplementaryInformation(_message.Message):
    __slots__ = ("loot_information", "waiting_for_help_information")
    LOOT_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    WAITING_FOR_HELP_INFORMATION_FIELD_NUMBER: _ClassVar[int]
    loot_information: TaxCollectorLootInformation
    waiting_for_help_information: TaxCollectorWaitingForHelpInformation
    def __init__(self, loot_information: _Optional[_Union[TaxCollectorLootInformation, _Mapping]] = ..., waiting_for_help_information: _Optional[_Union[TaxCollectorWaitingForHelpInformation, _Mapping]] = ...) -> None: ...

class TaxCollectorLootInformation(_message.Message):
    __slots__ = ("pods", "items_kamas_value")
    PODS_FIELD_NUMBER: _ClassVar[int]
    ITEMS_KAMAS_VALUE_FIELD_NUMBER: _ClassVar[int]
    pods: int
    items_kamas_value: int
    def __init__(self, pods: _Optional[int] = ..., items_kamas_value: _Optional[int] = ...) -> None: ...

class TaxCollectorWaitingForHelpInformation(_message.Message):
    __slots__ = ("time_left_before_fight", "placement_time_left", "defender_slots_left")
    TIME_LEFT_BEFORE_FIGHT_FIELD_NUMBER: _ClassVar[int]
    PLACEMENT_TIME_LEFT_FIELD_NUMBER: _ClassVar[int]
    DEFENDER_SLOTS_LEFT_FIELD_NUMBER: _ClassVar[int]
    time_left_before_fight: int
    placement_time_left: int
    defender_slots_left: int
    def __init__(self, time_left_before_fight: _Optional[int] = ..., placement_time_left: _Optional[int] = ..., defender_slots_left: _Optional[int] = ...) -> None: ...

class TaxCollectorOrderedSpell(_message.Message):
    __slots__ = ("spell_id", "slot_id")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    SLOT_ID_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    slot_id: int
    def __init__(self, spell_id: _Optional[int] = ..., slot_id: _Optional[int] = ...) -> None: ...

class TaxCollectorPreset(_message.Message):
    __slots__ = ("preset_uid", "spells", "characteristics")
    PRESET_UID_FIELD_NUMBER: _ClassVar[int]
    SPELLS_FIELD_NUMBER: _ClassVar[int]
    CHARACTERISTICS_FIELD_NUMBER: _ClassVar[int]
    preset_uid: str
    spells: _containers.RepeatedCompositeFieldContainer[TaxCollectorOrderedSpell]
    characteristics: _containers.RepeatedCompositeFieldContainer[CharacterCharacteristic]
    def __init__(self, preset_uid: _Optional[str] = ..., spells: _Optional[_Iterable[_Union[TaxCollectorOrderedSpell, _Mapping]]] = ..., characteristics: _Optional[_Iterable[_Union[CharacterCharacteristic, _Mapping]]] = ...) -> None: ...

class MountData(_message.Message):
    __slots__ = ("id", "model_id", "ancestors", "behaviors", "name", "gender", "owner_id", "experience", "experience_for_level", "experience_for_next_level", "level", "is_rideable", "max_pods", "is_wild", "stamina", "stamina_max", "maturity", "maturity_for_adult", "energy", "energy_max", "serenity", "aggressiveness_max", "serenity_max", "love", "love_max", "fertilization_time", "is_fertilization_ready", "boost_limiter", "boost_max", "reproduction_count", "reproduction_count_max", "harness_gid", "use_harness_colors", "effects")
    ID_FIELD_NUMBER: _ClassVar[int]
    MODEL_ID_FIELD_NUMBER: _ClassVar[int]
    ANCESTORS_FIELD_NUMBER: _ClassVar[int]
    BEHAVIORS_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    OWNER_ID_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_FOR_LEVEL_FIELD_NUMBER: _ClassVar[int]
    EXPERIENCE_FOR_NEXT_LEVEL_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    IS_RIDEABLE_FIELD_NUMBER: _ClassVar[int]
    MAX_PODS_FIELD_NUMBER: _ClassVar[int]
    IS_WILD_FIELD_NUMBER: _ClassVar[int]
    STAMINA_FIELD_NUMBER: _ClassVar[int]
    STAMINA_MAX_FIELD_NUMBER: _ClassVar[int]
    MATURITY_FIELD_NUMBER: _ClassVar[int]
    MATURITY_FOR_ADULT_FIELD_NUMBER: _ClassVar[int]
    ENERGY_FIELD_NUMBER: _ClassVar[int]
    ENERGY_MAX_FIELD_NUMBER: _ClassVar[int]
    SERENITY_FIELD_NUMBER: _ClassVar[int]
    AGGRESSIVENESS_MAX_FIELD_NUMBER: _ClassVar[int]
    SERENITY_MAX_FIELD_NUMBER: _ClassVar[int]
    LOVE_FIELD_NUMBER: _ClassVar[int]
    LOVE_MAX_FIELD_NUMBER: _ClassVar[int]
    FERTILIZATION_TIME_FIELD_NUMBER: _ClassVar[int]
    IS_FERTILIZATION_READY_FIELD_NUMBER: _ClassVar[int]
    BOOST_LIMITER_FIELD_NUMBER: _ClassVar[int]
    BOOST_MAX_FIELD_NUMBER: _ClassVar[int]
    REPRODUCTION_COUNT_FIELD_NUMBER: _ClassVar[int]
    REPRODUCTION_COUNT_MAX_FIELD_NUMBER: _ClassVar[int]
    HARNESS_GID_FIELD_NUMBER: _ClassVar[int]
    USE_HARNESS_COLORS_FIELD_NUMBER: _ClassVar[int]
    EFFECTS_FIELD_NUMBER: _ClassVar[int]
    id: int
    model_id: int
    ancestors: _containers.RepeatedScalarFieldContainer[int]
    behaviors: _containers.RepeatedScalarFieldContainer[int]
    name: str
    gender: Gender
    owner_id: int
    experience: int
    experience_for_level: int
    experience_for_next_level: int
    level: int
    is_rideable: bool
    max_pods: int
    is_wild: bool
    stamina: int
    stamina_max: int
    maturity: int
    maturity_for_adult: int
    energy: int
    energy_max: int
    serenity: int
    aggressiveness_max: int
    serenity_max: int
    love: int
    love_max: int
    fertilization_time: int
    is_fertilization_ready: bool
    boost_limiter: int
    boost_max: int
    reproduction_count: int
    reproduction_count_max: int
    harness_gid: int
    use_harness_colors: bool
    effects: _containers.RepeatedCompositeFieldContainer[ObjectEffect]
    def __init__(self, id: _Optional[int] = ..., model_id: _Optional[int] = ..., ancestors: _Optional[_Iterable[int]] = ..., behaviors: _Optional[_Iterable[int]] = ..., name: _Optional[str] = ..., gender: _Optional[_Union[Gender, str]] = ..., owner_id: _Optional[int] = ..., experience: _Optional[int] = ..., experience_for_level: _Optional[int] = ..., experience_for_next_level: _Optional[int] = ..., level: _Optional[int] = ..., is_rideable: bool = ..., max_pods: _Optional[int] = ..., is_wild: bool = ..., stamina: _Optional[int] = ..., stamina_max: _Optional[int] = ..., maturity: _Optional[int] = ..., maturity_for_adult: _Optional[int] = ..., energy: _Optional[int] = ..., energy_max: _Optional[int] = ..., serenity: _Optional[int] = ..., aggressiveness_max: _Optional[int] = ..., serenity_max: _Optional[int] = ..., love: _Optional[int] = ..., love_max: _Optional[int] = ..., fertilization_time: _Optional[int] = ..., is_fertilization_ready: bool = ..., boost_limiter: _Optional[int] = ..., boost_max: _Optional[int] = ..., reproduction_count: _Optional[int] = ..., reproduction_count_max: _Optional[int] = ..., harness_gid: _Optional[int] = ..., use_harness_colors: bool = ..., effects: _Optional[_Iterable[_Union[ObjectEffect, _Mapping]]] = ...) -> None: ...

class PaddockInformation(_message.Message):
    __slots__ = ("max_outdoor_mount", "max_items", "content", "instances")
    class PaddockContent(_message.Message):
        __slots__ = ("paddock_id", "coordinates", "abandoned", "mounts_information")
        class MountForPaddock(_message.Message):
            __slots__ = ("model_id", "name", "owner_name")
            MODEL_ID_FIELD_NUMBER: _ClassVar[int]
            NAME_FIELD_NUMBER: _ClassVar[int]
            OWNER_NAME_FIELD_NUMBER: _ClassVar[int]
            model_id: int
            name: str
            owner_name: str
            def __init__(self, model_id: _Optional[int] = ..., name: _Optional[str] = ..., owner_name: _Optional[str] = ...) -> None: ...
        PADDOCK_ID_FIELD_NUMBER: _ClassVar[int]
        COORDINATES_FIELD_NUMBER: _ClassVar[int]
        ABANDONED_FIELD_NUMBER: _ClassVar[int]
        MOUNTS_INFORMATION_FIELD_NUMBER: _ClassVar[int]
        paddock_id: int
        coordinates: MapExtendedCoordinates
        abandoned: bool
        mounts_information: _containers.RepeatedCompositeFieldContainer[PaddockInformation.PaddockContent.MountForPaddock]
        def __init__(self, paddock_id: _Optional[int] = ..., coordinates: _Optional[_Union[MapExtendedCoordinates, _Mapping]] = ..., abandoned: bool = ..., mounts_information: _Optional[_Iterable[_Union[PaddockInformation.PaddockContent.MountForPaddock, _Mapping]]] = ...) -> None: ...
    class PaddockInstances(_message.Message):
        __slots__ = ("paddocks_to_sell",)
        class PaddockToSell(_message.Message):
            __slots__ = ("price", "locked", "guild_information")
            class PaddockGuildInformation(_message.Message):
                __slots__ = ("deserted", "guild_information")
                DESERTED_FIELD_NUMBER: _ClassVar[int]
                GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
                deserted: bool
                guild_information: GuildInformation
                def __init__(self, deserted: bool = ..., guild_information: _Optional[_Union[GuildInformation, _Mapping]] = ...) -> None: ...
            PRICE_FIELD_NUMBER: _ClassVar[int]
            LOCKED_FIELD_NUMBER: _ClassVar[int]
            GUILD_INFORMATION_FIELD_NUMBER: _ClassVar[int]
            price: int
            locked: bool
            guild_information: PaddockInformation.PaddockInstances.PaddockToSell.PaddockGuildInformation
            def __init__(self, price: _Optional[int] = ..., locked: bool = ..., guild_information: _Optional[_Union[PaddockInformation.PaddockInstances.PaddockToSell.PaddockGuildInformation, _Mapping]] = ...) -> None: ...
        PADDOCKS_TO_SELL_FIELD_NUMBER: _ClassVar[int]
        paddocks_to_sell: _containers.RepeatedCompositeFieldContainer[PaddockInformation.PaddockInstances.PaddockToSell]
        def __init__(self, paddocks_to_sell: _Optional[_Iterable[_Union[PaddockInformation.PaddockInstances.PaddockToSell, _Mapping]]] = ...) -> None: ...
    MAX_OUTDOOR_MOUNT_FIELD_NUMBER: _ClassVar[int]
    MAX_ITEMS_FIELD_NUMBER: _ClassVar[int]
    CONTENT_FIELD_NUMBER: _ClassVar[int]
    INSTANCES_FIELD_NUMBER: _ClassVar[int]
    max_outdoor_mount: int
    max_items: int
    content: PaddockInformation.PaddockContent
    instances: PaddockInformation.PaddockInstances
    def __init__(self, max_outdoor_mount: _Optional[int] = ..., max_items: _Optional[int] = ..., content: _Optional[_Union[PaddockInformation.PaddockContent, _Mapping]] = ..., instances: _Optional[_Union[PaddockInformation.PaddockInstances, _Mapping]] = ...) -> None: ...

class SpellItem(_message.Message):
    __slots__ = ("spell_id", "spell_level", "available")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    SPELL_LEVEL_FIELD_NUMBER: _ClassVar[int]
    AVAILABLE_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    spell_level: int
    available: bool
    def __init__(self, spell_id: _Optional[int] = ..., spell_level: _Optional[int] = ..., available: bool = ...) -> None: ...

class SpellModifier(_message.Message):
    __slots__ = ("spell_id", "action_type", "modifier_type", "context", "equipment")
    SPELL_ID_FIELD_NUMBER: _ClassVar[int]
    ACTION_TYPE_FIELD_NUMBER: _ClassVar[int]
    MODIFIER_TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTEXT_FIELD_NUMBER: _ClassVar[int]
    EQUIPMENT_FIELD_NUMBER: _ClassVar[int]
    spell_id: int
    action_type: SpellModifierActionType
    modifier_type: SpellModifierType
    context: int
    equipment: int
    def __init__(self, spell_id: _Optional[int] = ..., action_type: _Optional[_Union[SpellModifierActionType, str]] = ..., modifier_type: _Optional[_Union[SpellModifierType, str]] = ..., context: _Optional[int] = ..., equipment: _Optional[int] = ...) -> None: ...
