import hashlib
import math
import os
import platform
import re
import subprocess
import sys

import psutil

if sys.platform == "win32":
    import pythoncom
    import wmi
else:
    wmi = None
    pythoncom = None


class Device:
    __uuid: str | None = None

    @staticmethod
    def getUUID():
        if Device.__uuid:
            return Device.__uuid

        plt = Device.getPlatform()
        arch = Device.getArch()
        machine_id = Device.getMachineId(plt, arch)
        cpu_count = Device.getCpuLength()
        cpu_model = Device.getCpuModel()

        Device.__uuid = ",".join([plt, arch, machine_id, str(cpu_count), cpu_model])
        return Device.__uuid

    @staticmethod
    def getMachineId(plt: str, arch: str, original: bool = False) -> str:
        try:
            cmd = Device.getGUIDCmdPerPlatform(plt, arch)
            output = subprocess.check_output(cmd, shell=True, text=True)
            machine_uuid = Device.parseMachineGuuid(plt, output)

            if original:
                return machine_uuid

            sha256_hash_machine_uuid = hashlib.sha256()
            sha256_hash_machine_uuid.update(machine_uuid.encode("utf-8"))
            return sha256_hash_machine_uuid.hexdigest()
        except subprocess.CalledProcessError as e:
            raise Exception("Error while obtaining machine id: " + str(e))

    @staticmethod
    def getGUIDCmdPerPlatform(plt: str, arch: str):
        cmd_per_platform = {
            "darwin": "ioreg -rd1 -c IOPlatformExpertDevice",
            "win32": (
                os.path.join(
                    "%windir%",
                    "sysnative"
                    if arch == "32bit" and "PROCESSOR_ARCHITEW6432" in os.environ
                    else "System32",
                )
                + "\\REG.exe QUERY HKEY_LOCAL_MACHINE\\SOFTWARE\\Microsoft\\Cryptography /v MachineGuid"
            ),
            "linux": "( cat /var/lib/dbus/machine-id /etc/machine-id 2> /dev/null || hostname ) | head -n 1 || :",
            "freebsd": "kenv -q smbios.system.uuid || sysctl -n kern.hostuuid",
        }

        return cmd_per_platform[plt]

    @staticmethod
    def parseMachineGuuid(plt: str, std_out: str) -> str:
        match plt:
            case "darwin":
                return re.sub(
                    r'=|\s+|"', "", std_out.split("IOPlatformUUID")[1].split("\n")[0]
                ).lower()
            case "win32":
                return re.sub(r"\r+|\n+|\s+", "", std_out.split("REG_SZ")[1]).lower()
            case "linux" | "freebsd":
                return re.sub(r"\r+|\n+|\s+", "", std_out).lower()
            case _:
                raise OSError

    @staticmethod
    def getArch():
        # Map Python's platform.machine() to JavaScript's os.arch() style
        arch_map = {"AMD64": "x64", "x86_64": "x64", "i386": "x86", "i686": "x86"}
        return arch_map[platform.machine()]

    @staticmethod
    def getPlatform():
        # Map Python's platform.system() to JavaScript's os.platform() style
        system_map = {"Windows": "win32", "Darwin": "darwin", "Linux": "linux"}
        plt = system_map[platform.system()]
        return plt

    @staticmethod
    def getCpuLength() -> int:
        return psutil.cpu_count(logical=True) or 0

    @staticmethod
    def getCpuModel() -> str:
        if psutil.WINDOWS:
            assert wmi and pythoncom
            pythoncom.CoInitialize()
            _wmi = wmi.WMI()
            cpu_info = _wmi.Win32_Processor()[0]
            cpu_model = cpu_info.Name
        elif psutil.LINUX or psutil.MACOS:
            with open("/proc/cpuinfo", "r") as file:
                for line in file:
                    if "model name" in line:
                        cpu_model = line.split(":")[1].strip()
                        break
                else:
                    raise ValueError("did not found model name cpu")
        else:
            raise OSError

        return cpu_model

    @staticmethod
    def getComputerRam():
        ram_mb = int(psutil.virtual_memory().total / (1024**2))
        return int(2 ** round(math.log(ram_mb, 2)))

    @staticmethod
    def getOsVersion():
        version_splitted = platform.version().split(".")
        major_version = version_splitted[0]
        medium_version = version_splitted[1]
        return float(f"{major_version}.{medium_version}")
