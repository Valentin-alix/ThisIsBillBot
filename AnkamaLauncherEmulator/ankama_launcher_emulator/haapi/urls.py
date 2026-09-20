from urllib.parse import urlencode

HAAPI_HOST = "haapi.ankama.com"

HAAPI_URL = f"https://{HAAPI_HOST}/"

ANKAMA_ACCOUNT_CREATE_TOKEN = HAAPI_URL + "json/Ankama/v5/Account/CreateToken"
ANKAMA_ACCOUNT_SET_NICKNAME_WITH_API_KEY = HAAPI_URL + "json/Ankama/v5/Account/SetNicknameWithApiKey"
ANKAMA_ACCOUNT_SIGN_ON_WITH_API_KEY = HAAPI_URL + "json/Ankama/v5/Account/SignOnWithApiKey"
ANKAMA_API_REFRESH_API_KEY = HAAPI_URL + "json/Ankama/v5/Api/RefreshApiKey"
ANKAMA_MONEY_OGRINS_ACCOUNT = HAAPI_URL + "json/Ankama/v5/Money/OgrinsAccount"
DOFUS_BAK_GET_OFFERS_OGRINES = HAAPI_URL + "json/Dofus/v3/Bak/Bid/GetOffersOgrines"
ANKAMA_SHIELD_SECURITY_CODE = HAAPI_URL + "json/Ankama/v5/Shield/SecurityCode"
ANKAMA_SHIELD_VALIDATE_CODE = HAAPI_URL + "json/Ankama/v5/Shield/ValidateCode"
ANKAMA_SHIELD_VALIDATE_OTP = HAAPI_URL + "json/Ankama/v5/Shield/ValidateOtp"
ANKAMA_SHOP_ACCESS_TOKEN = HAAPI_URL + "json/Ankama/v5/Shop/GetAccessTokenFromAnkamaApiKey"
ANKAMA_SHOP_API_URL = "https://shop-api.ankama.com"
ANKAMA_STORE_OVERLAY_AUTH_URL = "https://store.ankama.com/fr/overlay/auth"
ANKAMA_STORE_DOFUS_UNITY_INGAME_SHOP_KEY = "DOFUS_UNITY_INGAME"
REGISTER_FORM_URL = "https://auth.ankama.com/register/ankama/form"
ORIGIN_TRACKER = "https://www.ankama-launcher.com/dofus"
REDIRECT_URI = "https://auth.ankama.com/login-authorized"


def build_register_url(state: str | None = None) -> str:
    redirect_uri = REDIRECT_URI
    if state is not None:
        redirect_uri = f"{REDIRECT_URI}?state%3{state}"
    params = urlencode(
        {
            "origin_tracker": ORIGIN_TRACKER,
            "redirect_uri": redirect_uri,
        }
    )
    return f"{REGISTER_FORM_URL}?{params}"
