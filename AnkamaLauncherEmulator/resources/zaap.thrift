exception ZaapError {
  1: required i32 code,
  2: optional string details
}

enum ErrorCode {
  UNKNOWN = 1,
  UNAUTHORIZED = 2,
  INVALID_GAME_SESSION = 3,
  CONNECTION_FAILED = 1001,
  INVALID_CREDENTIALS = 1002,
  AUTH_NOT_LOGGED_IN = 2001,
  AUTH_BAN = 2002,
  AUTH_BLACKLIST = 2003,
  AUTH_LOCKED = 2004,
  AUTH_DELETED = 2005,
  AUTH_RESETANKAMA = 2006,
  AUTH_OTPTIMEFAILED = 2007,
  AUTH_SECURITYCARD = 2008,
  AUTH_BRUTEFORCE = 2009,
  AUTH_FAILED = 2010,
  AUTH_PARTNER = 2011,
  AUTH_MAILNOVALID = 2012,
  AUTH_BETACLOSED = 2013,
  AUTH_NOACCOUNT = 2014,
  AUTH_ACCOUNT_LINKED = 2015,
  AUTH_ACCOUNT_INVALID = 2016,
  AUTH_ACCOUNT_SHIELDED = 2017,
  UPDATER_CODE_RANGE = 3001,
  SETTINGS_KEY_NOT_FOUND = 4001,
  SETTINGS_INVALID_VALUE = 4002,
  USER_INFO_UNAVAILABLE = 5001
}

service ZaapService {
  string connect(1: string gameName, 2: string releaseName, 3: i32 instanceId, 4: string hash ) throws (1: ZaapError error),
  string auth_getGameToken(1: string gameSession, 2: i32 gameId) throws (1: ZaapError error),
  bool updater_isUpdateAvailable(1: string gameSession) throws (1: ZaapError error),
  string settings_get(1: string gameSession, 2: string key) throws (1: ZaapError error),
  void settings_set(1: string gameSession, 2: string key, 3: string value) throws (1: ZaapError error),
  string userInfo_get(1: string gameSession) throws (1: ZaapError error),
  void release_restartOnExit(1: string gameSession) throws (1: ZaapError error),
  void release_exitAndRepair(1: string gameSession) throws (1: ZaapError error),
  string zaapVersion_get(1: string gameSession) throws (1: ZaapError error),
  bool zaapMustUpdate_get(1: string gameSession) throws (1: ZaapError error),
  string auth_getGameTokenWithWindowId(1: string gameSession, 2: i32 gameId, 3: i32 windowId) throws (1: ZaapError error),
}