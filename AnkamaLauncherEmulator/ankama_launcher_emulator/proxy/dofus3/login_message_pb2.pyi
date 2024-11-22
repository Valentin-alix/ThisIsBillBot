from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class LoginMessage(_message.Message):
    __slots__ = ("request", "response", "event")
    REQUEST_FIELD_NUMBER: _ClassVar[int]
    RESPONSE_FIELD_NUMBER: _ClassVar[int]
    EVENT_FIELD_NUMBER: _ClassVar[int]
    request: Request
    response: Response
    event: Event
    def __init__(self, request: _Optional[_Union[Request, _Mapping]] = ..., response: _Optional[_Union[Response, _Mapping]] = ..., event: _Optional[_Union[Event, _Mapping]] = ...) -> None: ...

class Request(_message.Message):
    __slots__ = ("uuid", "ping", "identification", "selectServer", "forceAccount", "releaseAccount", "friend_list_request", "acquaintance_servers_request")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PING_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    SELECTSERVER_FIELD_NUMBER: _ClassVar[int]
    FORCEACCOUNT_FIELD_NUMBER: _ClassVar[int]
    RELEASEACCOUNT_FIELD_NUMBER: _ClassVar[int]
    FRIEND_LIST_REQUEST_FIELD_NUMBER: _ClassVar[int]
    ACQUAINTANCE_SERVERS_REQUEST_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    ping: Ping
    identification: IdentificationRequest
    selectServer: SelectServerRequest
    forceAccount: ForceAccountRequest
    releaseAccount: ReleaseAccountRequest
    friend_list_request: FriendListRequest
    acquaintance_servers_request: AcquaintanceServersRequest
    def __init__(self, uuid: _Optional[str] = ..., ping: _Optional[_Union[Ping, _Mapping]] = ..., identification: _Optional[_Union[IdentificationRequest, _Mapping]] = ..., selectServer: _Optional[_Union[SelectServerRequest, _Mapping]] = ..., forceAccount: _Optional[_Union[ForceAccountRequest, _Mapping]] = ..., releaseAccount: _Optional[_Union[ReleaseAccountRequest, _Mapping]] = ..., friend_list_request: _Optional[_Union[FriendListRequest, _Mapping]] = ..., acquaintance_servers_request: _Optional[_Union[AcquaintanceServersRequest, _Mapping]] = ...) -> None: ...

class Response(_message.Message):
    __slots__ = ("uuid", "pong", "identification", "selectServer", "forceAccount", "friend_list", "acquaintance_servers_response")
    UUID_FIELD_NUMBER: _ClassVar[int]
    PONG_FIELD_NUMBER: _ClassVar[int]
    IDENTIFICATION_FIELD_NUMBER: _ClassVar[int]
    SELECTSERVER_FIELD_NUMBER: _ClassVar[int]
    FORCEACCOUNT_FIELD_NUMBER: _ClassVar[int]
    FRIEND_LIST_FIELD_NUMBER: _ClassVar[int]
    ACQUAINTANCE_SERVERS_RESPONSE_FIELD_NUMBER: _ClassVar[int]
    uuid: str
    pong: Pong
    identification: IdentificationResponse
    selectServer: SelectServerResponse
    forceAccount: ForceAccountResponse
    friend_list: FriendListResponse
    acquaintance_servers_response: AcquaintanceServersResponse
    def __init__(self, uuid: _Optional[str] = ..., pong: _Optional[_Union[Pong, _Mapping]] = ..., identification: _Optional[_Union[IdentificationResponse, _Mapping]] = ..., selectServer: _Optional[_Union[SelectServerResponse, _Mapping]] = ..., forceAccount: _Optional[_Union[ForceAccountResponse, _Mapping]] = ..., friend_list: _Optional[_Union[FriendListResponse, _Mapping]] = ..., acquaintance_servers_response: _Optional[_Union[AcquaintanceServersResponse, _Mapping]] = ...) -> None: ...

class Event(_message.Message):
    __slots__ = ("server", "update_server_event")
    SERVER_FIELD_NUMBER: _ClassVar[int]
    UPDATE_SERVER_EVENT_FIELD_NUMBER: _ClassVar[int]
    server: Server
    update_server_event: UpdateServerEvent
    def __init__(self, server: _Optional[_Union[Server, _Mapping]] = ..., update_server_event: _Optional[_Union[UpdateServerEvent, _Mapping]] = ...) -> None: ...

class Ping(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class Pong(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class UpdateServerEvent(_message.Message):
    __slots__ = ("serverInformation",)
    SERVERINFORMATION_FIELD_NUMBER: _ClassVar[int]
    serverInformation: ServerInformation
    def __init__(self, serverInformation: _Optional[_Union[ServerInformation, _Mapping]] = ...) -> None: ...

class IdentificationRequest(_message.Message):
    __slots__ = ("device_identifier", "client_version", "tokenRequest", "loginRequest")
    DEVICE_IDENTIFIER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    TOKENREQUEST_FIELD_NUMBER: _ClassVar[int]
    LOGINREQUEST_FIELD_NUMBER: _ClassVar[int]
    device_identifier: str
    client_version: str
    tokenRequest: TokenRequest
    loginRequest: LoginRequest
    def __init__(self, device_identifier: _Optional[str] = ..., client_version: _Optional[str] = ..., tokenRequest: _Optional[_Union[TokenRequest, _Mapping]] = ..., loginRequest: _Optional[_Union[LoginRequest, _Mapping]] = ...) -> None: ...

class TokenRequest(_message.Message):
    __slots__ = ("token", "shield")
    class Shield(_message.Message):
        __slots__ = ("certificateId", "certificateHash")
        CERTIFICATEID_FIELD_NUMBER: _ClassVar[int]
        CERTIFICATEHASH_FIELD_NUMBER: _ClassVar[int]
        certificateId: int
        certificateHash: str
        def __init__(self, certificateId: _Optional[int] = ..., certificateHash: _Optional[str] = ...) -> None: ...
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    SHIELD_FIELD_NUMBER: _ClassVar[int]
    token: str
    shield: TokenRequest.Shield
    def __init__(self, token: _Optional[str] = ..., shield: _Optional[_Union[TokenRequest.Shield, _Mapping]] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ("login",)
    LOGIN_FIELD_NUMBER: _ClassVar[int]
    login: str
    def __init__(self, login: _Optional[str] = ...) -> None: ...

class IdentificationResponse(_message.Message):
    __slots__ = ("success", "error")
    class Success(_message.Message):
        __slots__ = ("account_id", "account_nickname", "account_tag", "server_list", "subscription_end_date", "rights", "fight_reconnection_server_id", "force_account_status")
        class Rights(_message.Message):
            __slots__ = ("show_force_account", "show_console", "unlimited_access", "infinite_subscription", "report", "esda")
            SHOW_FORCE_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
            SHOW_CONSOLE_FIELD_NUMBER: _ClassVar[int]
            UNLIMITED_ACCESS_FIELD_NUMBER: _ClassVar[int]
            INFINITE_SUBSCRIPTION_FIELD_NUMBER: _ClassVar[int]
            REPORT_FIELD_NUMBER: _ClassVar[int]
            ESDA_FIELD_NUMBER: _ClassVar[int]
            show_force_account: bool
            show_console: bool
            unlimited_access: bool
            infinite_subscription: bool
            report: bool
            esda: bool
            def __init__(self, show_force_account: bool = ..., show_console: bool = ..., unlimited_access: bool = ..., infinite_subscription: bool = ..., report: bool = ..., esda: bool = ...) -> None: ...
        ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
        ACCOUNT_NICKNAME_FIELD_NUMBER: _ClassVar[int]
        ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
        SERVER_LIST_FIELD_NUMBER: _ClassVar[int]
        SUBSCRIPTION_END_DATE_FIELD_NUMBER: _ClassVar[int]
        RIGHTS_FIELD_NUMBER: _ClassVar[int]
        FIGHT_RECONNECTION_SERVER_ID_FIELD_NUMBER: _ClassVar[int]
        FORCE_ACCOUNT_STATUS_FIELD_NUMBER: _ClassVar[int]
        account_id: int
        account_nickname: str
        account_tag: str
        server_list: ServerList
        subscription_end_date: str
        rights: IdentificationResponse.Success.Rights
        fight_reconnection_server_id: int
        force_account_status: ForceAccountStatus
        def __init__(self, account_id: _Optional[int] = ..., account_nickname: _Optional[str] = ..., account_tag: _Optional[str] = ..., server_list: _Optional[_Union[ServerList, _Mapping]] = ..., subscription_end_date: _Optional[str] = ..., rights: _Optional[_Union[IdentificationResponse.Success.Rights, _Mapping]] = ..., fight_reconnection_server_id: _Optional[int] = ..., force_account_status: _Optional[_Union[ForceAccountStatus, _Mapping]] = ...) -> None: ...
    class Error(_message.Message):
        __slots__ = ("reason", "ban_end_date", "required_version")
        class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN_AUTH_ERROR: _ClassVar[IdentificationResponse.Error.Reason]
            ALREADY_CONNECTED: _ClassVar[IdentificationResponse.Error.Reason]
            OTP_TIMEOUT: _ClassVar[IdentificationResponse.Error.Reason]
            BANNED: _ClassVar[IdentificationResponse.Error.Reason]
            INVALID_SHIELD_CERTIFICATE: _ClassVar[IdentificationResponse.Error.Reason]
            LOCKED: _ClassVar[IdentificationResponse.Error.Reason]
            CREDENTIALS_RESET: _ClassVar[IdentificationResponse.Error.Reason]
            WRONG_CREDENTIALS: _ClassVar[IdentificationResponse.Error.Reason]
            EMAIL_UNVALIDATED: _ClassVar[IdentificationResponse.Error.Reason]
            ANONYMOUS_IP_FORBIDDEN: _ClassVar[IdentificationResponse.Error.Reason]
            NICKNAME_REGISTRATION: _ClassVar[IdentificationResponse.Error.Reason]
            UNAUTHORIZED: _ClassVar[IdentificationResponse.Error.Reason]
            INVALID_CLIENT_VERSION: _ClassVar[IdentificationResponse.Error.Reason]
            OUTDATED_CLIENT_VERSION: _ClassVar[IdentificationResponse.Error.Reason]
        UNKNOWN_AUTH_ERROR: IdentificationResponse.Error.Reason
        ALREADY_CONNECTED: IdentificationResponse.Error.Reason
        OTP_TIMEOUT: IdentificationResponse.Error.Reason
        BANNED: IdentificationResponse.Error.Reason
        INVALID_SHIELD_CERTIFICATE: IdentificationResponse.Error.Reason
        LOCKED: IdentificationResponse.Error.Reason
        CREDENTIALS_RESET: IdentificationResponse.Error.Reason
        WRONG_CREDENTIALS: IdentificationResponse.Error.Reason
        EMAIL_UNVALIDATED: IdentificationResponse.Error.Reason
        ANONYMOUS_IP_FORBIDDEN: IdentificationResponse.Error.Reason
        NICKNAME_REGISTRATION: IdentificationResponse.Error.Reason
        UNAUTHORIZED: IdentificationResponse.Error.Reason
        INVALID_CLIENT_VERSION: IdentificationResponse.Error.Reason
        OUTDATED_CLIENT_VERSION: IdentificationResponse.Error.Reason
        REASON_FIELD_NUMBER: _ClassVar[int]
        BAN_END_DATE_FIELD_NUMBER: _ClassVar[int]
        REQUIRED_VERSION_FIELD_NUMBER: _ClassVar[int]
        reason: IdentificationResponse.Error.Reason
        ban_end_date: str
        required_version: str
        def __init__(self, reason: _Optional[_Union[IdentificationResponse.Error.Reason, str]] = ..., ban_end_date: _Optional[str] = ..., required_version: _Optional[str] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: IdentificationResponse.Success
    error: IdentificationResponse.Error
    def __init__(self, success: _Optional[_Union[IdentificationResponse.Success, _Mapping]] = ..., error: _Optional[_Union[IdentificationResponse.Error, _Mapping]] = ...) -> None: ...

class SelectServerRequest(_message.Message):
    __slots__ = ("server",)
    SERVER_FIELD_NUMBER: _ClassVar[int]
    server: int
    def __init__(self, server: _Optional[int] = ...) -> None: ...

class SelectServerResponse(_message.Message):
    __slots__ = ("success", "error")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        REFUSED: _ClassVar[SelectServerResponse.Error]
        SUBSCRIBER_ONLY: _ClassVar[SelectServerResponse.Error]
        SINGLE_ACCOUNT_VERIFIED_ONLY: _ClassVar[SelectServerResponse.Error]
        MAINTENANCE: _ClassVar[SelectServerResponse.Error]
    REFUSED: SelectServerResponse.Error
    SUBSCRIBER_ONLY: SelectServerResponse.Error
    SINGLE_ACCOUNT_VERIFIED_ONLY: SelectServerResponse.Error
    MAINTENANCE: SelectServerResponse.Error
    class Success(_message.Message):
        __slots__ = ("token", "host", "ports")
        TOKEN_FIELD_NUMBER: _ClassVar[int]
        HOST_FIELD_NUMBER: _ClassVar[int]
        PORTS_FIELD_NUMBER: _ClassVar[int]
        token: str
        host: str
        ports: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, token: _Optional[str] = ..., host: _Optional[str] = ..., ports: _Optional[_Iterable[int]] = ...) -> None: ...
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: SelectServerResponse.Success
    error: SelectServerResponse.Error
    def __init__(self, success: _Optional[_Union[SelectServerResponse.Success, _Mapping]] = ..., error: _Optional[_Union[SelectServerResponse.Error, str]] = ...) -> None: ...

class ServerList(_message.Message):
    __slots__ = ("servers", "max_slot_by_type", "ctip")
    SERVERS_FIELD_NUMBER: _ClassVar[int]
    MAX_SLOT_BY_TYPE_FIELD_NUMBER: _ClassVar[int]
    CTIP_FIELD_NUMBER: _ClassVar[int]
    servers: _containers.RepeatedCompositeFieldContainer[ServerInformation]
    max_slot_by_type: int
    ctip: bool
    def __init__(self, servers: _Optional[_Iterable[_Union[ServerInformation, _Mapping]]] = ..., max_slot_by_type: _Optional[int] = ..., ctip: bool = ...) -> None: ...

class ServerInformation(_message.Message):
    __slots__ = ("server", "accessibility", "characters")
    class Accessibility(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ACCESSIBLE: _ClassVar[ServerInformation.Accessibility]
        SUBSCRIBE_RESTRICTION: _ClassVar[ServerInformation.Accessibility]
        MONO_ACCOUNT_RESTRICTION: _ClassVar[ServerInformation.Accessibility]
        UNKNOWN: _ClassVar[ServerInformation.Accessibility]
    ACCESSIBLE: ServerInformation.Accessibility
    SUBSCRIBE_RESTRICTION: ServerInformation.Accessibility
    MONO_ACCOUNT_RESTRICTION: ServerInformation.Accessibility
    UNKNOWN: ServerInformation.Accessibility
    SERVER_FIELD_NUMBER: _ClassVar[int]
    ACCESSIBILITY_FIELD_NUMBER: _ClassVar[int]
    CHARACTERS_FIELD_NUMBER: _ClassVar[int]
    server: Server
    accessibility: ServerInformation.Accessibility
    characters: _containers.RepeatedCompositeFieldContainer[CharacterInformation]
    def __init__(self, server: _Optional[_Union[Server, _Mapping]] = ..., accessibility: _Optional[_Union[ServerInformation.Accessibility, str]] = ..., characters: _Optional[_Iterable[_Union[CharacterInformation, _Mapping]]] = ...) -> None: ...

class Server(_message.Message):
    __slots__ = ("id", "status", "mono_account", "esfj")
    class Status(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        ONLINE: _ClassVar[Server.Status]
        MAINTENANCE: _ClassVar[Server.Status]
    ONLINE: Server.Status
    MAINTENANCE: Server.Status
    ID_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    MONO_ACCOUNT_FIELD_NUMBER: _ClassVar[int]
    ESFJ_FIELD_NUMBER: _ClassVar[int]
    id: int
    status: Server.Status
    mono_account: bool
    esfj: bool
    def __init__(self, id: _Optional[int] = ..., status: _Optional[_Union[Server.Status, str]] = ..., mono_account: bool = ..., esfj: bool = ...) -> None: ...

class ForceAccountRequest(_message.Message):
    __slots__ = ("account_id",)
    ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    account_id: int
    def __init__(self, account_id: _Optional[int] = ...) -> None: ...

class ForceAccountResponse(_message.Message):
    __slots__ = ("success", "error")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    success: ForceAccountStatus
    error: ForceAccountError
    def __init__(self, success: _Optional[_Union[ForceAccountStatus, _Mapping]] = ..., error: _Optional[_Union[ForceAccountError, _Mapping]] = ...) -> None: ...

class ForceAccountStatus(_message.Message):
    __slots__ = ("is_forced", "forced_account_id", "forced_account_nickname", "forced_account_tag", "server_list")
    IS_FORCED_FIELD_NUMBER: _ClassVar[int]
    FORCED_ACCOUNT_ID_FIELD_NUMBER: _ClassVar[int]
    FORCED_ACCOUNT_NICKNAME_FIELD_NUMBER: _ClassVar[int]
    FORCED_ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
    SERVER_LIST_FIELD_NUMBER: _ClassVar[int]
    is_forced: bool
    forced_account_id: int
    forced_account_nickname: str
    forced_account_tag: str
    server_list: ServerList
    def __init__(self, is_forced: bool = ..., forced_account_id: _Optional[int] = ..., forced_account_nickname: _Optional[str] = ..., forced_account_tag: _Optional[str] = ..., server_list: _Optional[_Union[ServerList, _Mapping]] = ...) -> None: ...

class ForceAccountError(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class ReleaseAccountRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class CharacterInformation(_message.Message):
    __slots__ = ("name", "breed", "gender", "level", "last_connection_date")
    class Gender(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        MALE: _ClassVar[CharacterInformation.Gender]
        FEMALE: _ClassVar[CharacterInformation.Gender]
    MALE: CharacterInformation.Gender
    FEMALE: CharacterInformation.Gender
    class Breed(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        FECA: _ClassVar[CharacterInformation.Breed]
        OSAMODAS: _ClassVar[CharacterInformation.Breed]
        ENUTROF: _ClassVar[CharacterInformation.Breed]
        SRAM: _ClassVar[CharacterInformation.Breed]
        XELOR: _ClassVar[CharacterInformation.Breed]
        ECAFLIP: _ClassVar[CharacterInformation.Breed]
        ENIRIPSA: _ClassVar[CharacterInformation.Breed]
        IOP: _ClassVar[CharacterInformation.Breed]
        CRA: _ClassVar[CharacterInformation.Breed]
        SADIDA: _ClassVar[CharacterInformation.Breed]
        SACRIER: _ClassVar[CharacterInformation.Breed]
        PANDAWA: _ClassVar[CharacterInformation.Breed]
        ROGUE: _ClassVar[CharacterInformation.Breed]
        MASQUERAIDER: _ClassVar[CharacterInformation.Breed]
        FOGGERNAUTS: _ClassVar[CharacterInformation.Breed]
        ELIOTROPE: _ClassVar[CharacterInformation.Breed]
        HUPPERMAGE: _ClassVar[CharacterInformation.Breed]
        OUGINAK: _ClassVar[CharacterInformation.Breed]
        FORGELANCE: _ClassVar[CharacterInformation.Breed]
    FECA: CharacterInformation.Breed
    OSAMODAS: CharacterInformation.Breed
    ENUTROF: CharacterInformation.Breed
    SRAM: CharacterInformation.Breed
    XELOR: CharacterInformation.Breed
    ECAFLIP: CharacterInformation.Breed
    ENIRIPSA: CharacterInformation.Breed
    IOP: CharacterInformation.Breed
    CRA: CharacterInformation.Breed
    SADIDA: CharacterInformation.Breed
    SACRIER: CharacterInformation.Breed
    PANDAWA: CharacterInformation.Breed
    ROGUE: CharacterInformation.Breed
    MASQUERAIDER: CharacterInformation.Breed
    FOGGERNAUTS: CharacterInformation.Breed
    ELIOTROPE: CharacterInformation.Breed
    HUPPERMAGE: CharacterInformation.Breed
    OUGINAK: CharacterInformation.Breed
    FORGELANCE: CharacterInformation.Breed
    NAME_FIELD_NUMBER: _ClassVar[int]
    BREED_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    LEVEL_FIELD_NUMBER: _ClassVar[int]
    LAST_CONNECTION_DATE_FIELD_NUMBER: _ClassVar[int]
    name: str
    breed: CharacterInformation.Breed
    gender: CharacterInformation.Gender
    level: int
    last_connection_date: str
    def __init__(self, name: _Optional[str] = ..., breed: _Optional[_Union[CharacterInformation.Breed, str]] = ..., gender: _Optional[_Union[CharacterInformation.Gender, str]] = ..., level: _Optional[int] = ..., last_connection_date: _Optional[str] = ...) -> None: ...

class FriendListRequest(_message.Message):
    __slots__ = ()
    def __init__(self) -> None: ...

class FriendListResponse(_message.Message):
    __slots__ = ("friends", "error")
    class Error(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNKNOWN: _ClassVar[FriendListResponse.Error]
        FLOODING: _ClassVar[FriendListResponse.Error]
    UNKNOWN: FriendListResponse.Error
    FLOODING: FriendListResponse.Error
    class FriendList(_message.Message):
        __slots__ = ("friends",)
        class Friend(_message.Message):
            __slots__ = ("account_name", "account_tag", "servers")
            ACCOUNT_NAME_FIELD_NUMBER: _ClassVar[int]
            ACCOUNT_TAG_FIELD_NUMBER: _ClassVar[int]
            SERVERS_FIELD_NUMBER: _ClassVar[int]
            account_name: str
            account_tag: str
            servers: _containers.RepeatedScalarFieldContainer[int]
            def __init__(self, account_name: _Optional[str] = ..., account_tag: _Optional[str] = ..., servers: _Optional[_Iterable[int]] = ...) -> None: ...
        FRIENDS_FIELD_NUMBER: _ClassVar[int]
        friends: _containers.RepeatedCompositeFieldContainer[FriendListResponse.FriendList.Friend]
        def __init__(self, friends: _Optional[_Iterable[_Union[FriendListResponse.FriendList.Friend, _Mapping]]] = ...) -> None: ...
    FRIENDS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    friends: FriendListResponse.FriendList
    error: FriendListResponse.Error
    def __init__(self, friends: _Optional[_Union[FriendListResponse.FriendList, _Mapping]] = ..., error: _Optional[_Union[FriendListResponse.Error, str]] = ...) -> None: ...

class AcquaintanceServersRequest(_message.Message):
    __slots__ = ("name", "tag")
    NAME_FIELD_NUMBER: _ClassVar[int]
    TAG_FIELD_NUMBER: _ClassVar[int]
    name: str
    tag: str
    def __init__(self, name: _Optional[str] = ..., tag: _Optional[str] = ...) -> None: ...

class AcquaintanceServersResponse(_message.Message):
    __slots__ = ("servers", "error")
    class Servers(_message.Message):
        __slots__ = ("servers",)
        SERVERS_FIELD_NUMBER: _ClassVar[int]
        servers: _containers.RepeatedScalarFieldContainer[int]
        def __init__(self, servers: _Optional[_Iterable[int]] = ...) -> None: ...
    class Error(_message.Message):
        __slots__ = ("reason",)
        class Reason(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
            __slots__ = ()
            UNKNOWN: _ClassVar[AcquaintanceServersResponse.Error.Reason]
            NO_RESULT: _ClassVar[AcquaintanceServersResponse.Error.Reason]
            FLOOD: _ClassVar[AcquaintanceServersResponse.Error.Reason]
            INVALID_ACCOUNT: _ClassVar[AcquaintanceServersResponse.Error.Reason]
        UNKNOWN: AcquaintanceServersResponse.Error.Reason
        NO_RESULT: AcquaintanceServersResponse.Error.Reason
        FLOOD: AcquaintanceServersResponse.Error.Reason
        INVALID_ACCOUNT: AcquaintanceServersResponse.Error.Reason
        REASON_FIELD_NUMBER: _ClassVar[int]
        reason: AcquaintanceServersResponse.Error.Reason
        def __init__(self, reason: _Optional[_Union[AcquaintanceServersResponse.Error.Reason, str]] = ...) -> None: ...
    SERVERS_FIELD_NUMBER: _ClassVar[int]
    ERROR_FIELD_NUMBER: _ClassVar[int]
    servers: AcquaintanceServersResponse.Servers
    error: AcquaintanceServersResponse.Error
    def __init__(self, servers: _Optional[_Union[AcquaintanceServersResponse.Servers, _Mapping]] = ..., error: _Optional[_Union[AcquaintanceServersResponse.Error, _Mapping]] = ...) -> None: ...
