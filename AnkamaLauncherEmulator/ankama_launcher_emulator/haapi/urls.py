HAAPI_HOST = "haapi.ankama.com"

HAAPI_URL = f"https://{HAAPI_HOST}/"

ANKAMA_ACCOUNT_ACCOUNT = HAAPI_URL + "json/Ankama/v5/Account/Account"
ANKAMA_ACCOUNT_CREATE_TOKEN = HAAPI_URL + "json/Ankama/v5/Account/CreateToken"
ANKAMA_ACCOUNT_ORIGIN_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Account/OriginWithApiKey"
)
ANKAMA_ACCOUNT_SEND_DEVICE_INFOS = HAAPI_URL + "json/Ankama/v5/Account/SendDeviceInfos"
ANKAMA_ACCOUNT_SEND_MAIL_VALIDATION = (
    HAAPI_URL + "json/Ankama/v5/Account/SendMailValidation"
)
ANKAMA_ACCOUNT_SET_EMAIL = HAAPI_URL + "json/Ankama/v5/Account/SetEmail"
ANKAMA_ACCOUNT_SET_NICKNAME_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Account/SetNicknameWithApiKey"
)
ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Account/SignOnWithApiKey"
)
ANKAMA_ACCOUNT_SET_IDENTITY_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Account/SetIdentityWithApiKey"
)
ANKAMA_ACCOUNT_STATUS = HAAPI_URL + "json/Ankama/v5/Account/Status"
ANKAMA_API_CREATE_API_KEY = HAAPI_URL + "json/Ankama/v5/Api/CreateApiKey"
ANKAMA_API_DELETE_API_KEY = HAAPI_URL + "json/Ankama/v5/Api/DeleteApiKey"
ANKAMA_API_REFRESH_API_KEY = HAAPI_URL + "json/Ankama/v5/Api/RefreshApiKey"
ANKAMA_CMS_ITEMS_GET = HAAPI_URL + "json/Ankama/v5/Cms/Items/Get"
ANKAMA_CMS_ITEMS_CAROUSEL_GET = (
    HAAPI_URL + "json/Ankama/v5/Cms/Items/Carousel/GetForLauncher"
)
ANKAMA_CMS_ITEMS_GETBYID = HAAPI_URL + "json/Ankama/v5/Cms/Items/GetById"
ANKAMA_CMS_POLLINGAME_GET = HAAPI_URL + "json/Ankama/v5/Cms/PollInGame/Get"
ANKAMA_CMS_POLLINGAME_MARKASREAD = (
    HAAPI_URL + "json/Ankama/v5/Cms/PollInGame/MarkAsRead"
)
ANKAMA_GAME_END_SESSION_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Game/EndSessionWithApiKey"
)
ANKAMA_GAME_LIST_WITH_API_KEY = HAAPI_URL + "json/Ankama/v5/Game/ListWithApiKey"
ANKAMA_GAME_SEND_EVENTS = HAAPI_URL + "json/Ankama/v5/Game/SendEvents"
ANKAMA_GAME_START_SESSION_WITH_API_KEY = (
    HAAPI_URL + "json/Ankama/v5/Game/StartSessionWithApiKey"
)
ANKAMA_LEGALS_SET_TOU_VERSION = HAAPI_URL + "json/Ankama/v5/Legals/SetTouVersion"
ANKAMA_LEGALS_TOU = HAAPI_URL + "json/Ankama/v5/Legals/Tou"
ANKAMA_MONEY_OGRINS_AMOUNT = HAAPI_URL + "json/Ankama/v5/Money/OgrinsAmount"
ANKAMA_PREMIUM_GAME_CONNECT = HAAPI_URL + "json/Ankama/v5/Game/Premium/Session/Connect"
ANKAMA_PREMIUM_GAME_DISCONNECT = (
    HAAPI_URL + "json/Ankama/v5/Game/Premium/Session/Disconnect"
)
ANKAMA_PROVIDER_API_KEY_LINK = HAAPI_URL + "json/Ankama/v5/Provider/ApiKeyLink"
ANKAMA_PROVIDER_API_KEY_LOGIN = HAAPI_URL + "json/Ankama/v5/Provider/ApiKeyLogin"
ANKAMA_PROVIDER_GHOST_CREATE = HAAPI_URL + "json/Ankama/v5/Provider/ApiKeyGhostCreate"
ANKAMA_SHIELD_SECURITY_CODE = HAAPI_URL + "json/Ankama/v5/Shield/SecurityCode"
ANKAMA_SHIELD_VALIDATE_CODE = HAAPI_URL + "json/Ankama/v5/Shield/ValidateCode"
ANKAMA_SHOP_ARTICLES_LIST_BY_CATEGORY = (
    HAAPI_URL + "json/Ankama/v5/Shop/ArticlesListByCategory"
)
ANKAMA_SHOP_CATEGORIES_LIST = HAAPI_URL + "json/Ankama/v5/Shop/CategoriesList"
ANKAMA_SHOP_SIMPLE_BUY = HAAPI_URL + "json/Ankama/v5/Shop/SimpleBuy"
ANKAMA_SHOP_ARTICLE_LIST_BY_ID = HAAPI_URL + "json/Ankama/v5/Shop/ArticlesListByIds"
ANKAMA_VOD_ACCESS_TOKEN_GET = (
    HAAPI_URL + "json/Ankama/v5/Vod/AccessToken/GetAccessToken"
)
