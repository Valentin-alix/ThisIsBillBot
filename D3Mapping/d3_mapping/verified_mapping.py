from D3Mapping.d3_mapping.models.verified_mapping import VerifiedMapping

GAME_VERIFIED_MAPPING_BY_OBF: dict[str, str] = {
    "gsr": "GameMessage",
    "hbo": "SpellsEvent",  # 12728
    "hxl": "InventoryContentEvent",
    "jrl": "CharacterCharacteristicsEvent",
    "jtx": "CharacterSelectionEvent",  #
    "iaa": "InventoryWeightEvent",
    "hcm": "ZaapKnownListEvent",  # 191105026 (zaap astrub)
    "hvv": "JobExperiencesUpdateEvent",
    "iny": "MapCurrentEvent",
    "iou": "MapComplementaryInformationEvent",
    "ipi": "MapMovementRequest",
    "ion": "MapMovementEvent",
    "inq": "MapMovementConfirmRequest",
    "ipa": "MapMovementConfirmResponse",
    "ioh": "MapChangeRequest",
    "iah": "InteractiveUseRequest",
    "iao": "StatedElementUpdatedEvent",
    "iam": "InteractiveUsedEvent",
    "hqs": "NpcGenericActionRequest",
    "hrc": "NpcDialogQuestionEvent",
    "hqt": "NpcDialogReplyRequest",
    "izi": "ExchangeStartedWithStorageEvent",  # 2147483647 (cest le max slot)
    "hzo": "StorageInventoryContentEvent",
    "jas": "ExchangeObjectTransferAllFromInventoryRequest",
    "jal": "ExchangeObjectMoveRequest",
    "hxz": "ObjectAddedEvent",
    "hzg": "ObjectQuantityEvent",
    "iyu": "ExchangeMoveKamaRequest",
    "jja": "DialogLeaveRequest",
    "jce": "ExchangeLeaveEvent",
    # "idb": "HavenBagEnterRequest",
    # "iee": "HavenBagExitRequest",
    # "iah": "ObjectUseRequest",
    # "gxk": "TeleportRequest",
    # # # sale hotel
    "jbb": "ExchangeBidSellerStartedEvent",
    "jdd": "ExchangeBidHouseSearchRequest",
    "jaw": "ExchangeBidHousePriceRequest",
    "jaf": "ExchangeBidPriceEvent",
    "jcb": "ExchangeObjectMovePricedRequest",
    "jcd": "ExchangeObjectModifyPricedRequest",
    "jcx": "ExchangeBidHouseItemRemovedEvent",
    "ize": "ExchangeBidHouseItemAddedEvent",
    "kme": "TextInformationEvent",
    # fight
    "heb": "AttackMonsterRequest",
    "iqe": "FightMapInformationEvent",
    "ixs": "FightPlacementPossiblePositionsEvent",
    "ixu": "FightPlacementPositionRequest",
    "ixr": "FightReadyRequest",
    "ium": "FightTurnStartPlayingEvent",
    "iqn": "GameActionFightCastRequest",
    "iue": "GameActionFightEvent",
    "iql": "SequenceEndEvent",
    "iqo": "GameActionAcknowledgementRequest",
    "ivl": "FightLiveStateEvent",
    "iwk": "FightTurnFinishRequest",
    "jkr": "EntitiesDispositionEvent",
    "iul": "FightRefreshCharacterStatsEvent",
    "ipd": "MapMovementRefusedEvent",
    "jra": "ChatChannelMessageRequest",
    # "jrl": "ChatPrivateMessageRequest",
    # "jrm": "ChatChannelMessageEvent",
    # "ijg": "GuildMembershipEvent",  # Farm-Land
    # "ind": "GuildChestCurrentListenersAddEvent",
    # "jdl": "ExchangeStartedWithMultiTabStorageEvent",
    # "inf": "GuildChestTabSelectRequest",
    # "jcu": "ExchangeCraftStartedEvent",  # 1 champs (le skill id)
    # "jcn": "ExchangeSetCraftRecipeRequest",
    # "izl": "ExchangeCraftCountRequest",
    # "jbr": "ExchangeCraftCountModifiedEvent",
    # "jfz": "ExchangeReadyRequest",
    # "iba": "InteractiveUseErrorEvent",
    # "jft": "ObjectAveragePricesEvent",
    # CharacterCharacteristicUpgradeRequest
    # CharacterLevelUpEvent
    # "jbl": "ExchangeBidBuyerStartedEvent",
    # "jcd": "ExchangeBidHouseTypeRequest",
    # "jeu": "ExchangeTypesExchangerDescriptionForUserEvent",
    # "jet": "ExchangeTypesItemsExchangerDescriptionForUserEvent",
    "jol": "IdentificationRequest",
}
GAME_MAPPING_FIELDS: dict[str, dict[str, str]] = {
    "GameMessage": {"request": "eyry", "event": "eyrx"},
    # "InteractiveUseRequest": {"element_id": "fdlu"},
    # "InteractiveElement": {"enabled_skills": "flsr"},
    "GameActionFightEvent": {
        "slide": "fgyj",
        # "exchange_positions": "fgkn",
        # "teleport_on_same_map": "fgkm",
    },
}

GAME_VERIFIED_MAPPING = VerifiedMapping(
    verified_msg_by_obf=GAME_VERIFIED_MAPPING_BY_OBF,
    field_mappings=GAME_MAPPING_FIELDS,
)
