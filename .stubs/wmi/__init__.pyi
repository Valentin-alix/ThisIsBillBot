class _Processor:
    Name: str


class _WMIClient:
    def Win32_Processor(self) -> list[_Processor]: ...


def WMI(
    computer: str = "",
    impersonation_level: str = "",
    authentication_level: str = "",
    authority: str = "",
    privileges: str = "",
    moniker: str = "",
    wmi: None = None,
    namespace: str = "",
    suffix: str = "",
    user: str = "",
    password: str = "",
    find_classes: bool = False,
    debug: bool = False,
) -> _WMIClient: ...
