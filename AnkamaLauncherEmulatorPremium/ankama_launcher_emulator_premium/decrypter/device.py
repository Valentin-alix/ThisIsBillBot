import getpass
import hashlib
import math
import os
import platform
import subprocess
import sys
from pathlib import Path

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
    def getUUID() -> str:
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
            machine_uuid = Device.getMachineGuid(plt, arch)

            if original:
                return machine_uuid

            sha256_hash_machine_uuid = hashlib.sha256()
            sha256_hash_machine_uuid.update(machine_uuid.encode("utf-8"))
            return sha256_hash_machine_uuid.hexdigest()
        except subprocess.CalledProcessError as error:
            raise RuntimeError("Error while obtaining machine id: " + str(error)) from error

    @staticmethod
    def getMachineGuid(plt: str, arch: str) -> str:
        match plt:
            case "win32":
                reg_exe = Device.getWindowsRegExecutable(arch)
                output = subprocess.check_output(
                    [
                        str(reg_exe),
                        "QUERY",
                        r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Cryptography",
                        "/v",
                        "MachineGuid",
                    ],
                    text=True,
                )
                return Device.parseMachineGuuid(plt, output)
            case "linux":
                for machine_id_path in (
                    Path("/var/lib/dbus/machine-id"),
                    Path("/etc/machine-id"),
                ):
                    if machine_id_path.exists():
                        machine_id = machine_id_path.read_text(encoding="utf-8").strip()
                        if machine_id:
                            return machine_id.lower()
                return platform.node().strip().lower()
            case _:
                raise OSError(f"Unsupported platform: {plt}")

    @staticmethod
    def getWindowsRegExecutable(arch: str) -> Path:
        windows_dir = Path(os.environ.get("windir", r"C:\Windows"))
        system_dir = "sysnative" if arch == "x86" and "PROCESSOR_ARCHITEW6432" in os.environ else "System32"
        return windows_dir / system_dir / "REG.exe"

    @staticmethod
    def parseMachineGuuid(plt: str, std_out: str) -> str:
        match plt:
            case "darwin":
                return (
                    "".join(std_out.split("IOPlatformUUID")[1].split("\n")[0].split())
                    .replace("=", "")
                    .replace('"', "")
                    .lower()
                )
            case "win32":
                return "".join(std_out.split("REG_SZ")[1].split()).lower()
            case "linux" | "freebsd":
                return "".join(std_out.split()).lower()
            case _:
                raise OSError

    @staticmethod
    def getArch() -> str:
        # Map Python's platform.machine() to JavaScript's os.arch() style
        arch_map = {"AMD64": "x64", "x86_64": "x64", "i386": "x86", "i686": "x86"}
        machine = platform.machine()
        if machine not in arch_map:
            raise OSError(f"Unsupported architecture: {machine}")
        return arch_map[machine]

    @staticmethod
    def getPlatform() -> str:
        # Map Python's platform.system() to JavaScript's os.platform() style
        system_map = {"Windows": "win32", "Darwin": "darwin", "Linux": "linux"}
        system = platform.system()
        if system not in system_map:
            raise OSError(f"Unsupported platform: {system}")
        return system_map[system]

    @staticmethod
    def getCpuLength() -> int:
        return psutil.cpu_count(logical=True) or 0

    @staticmethod
    def getCpuModel() -> str:
        if psutil.WINDOWS:
            if wmi is None or pythoncom is None:
                raise RuntimeError("WMI is unavailable on this system")
            pythoncom.CoInitialize()
            wmi_client = wmi.WMI()
            cpu_info = wmi_client.Win32_Processor()[0]
            cpu_model = cpu_info.Name
        elif psutil.LINUX:
            with open("/proc/cpuinfo", encoding="utf-8") as file:
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
    def getComputerRam() -> int:
        ram_mb = int(psutil.virtual_memory().total / (1024**2))
        return int(2 ** round(math.log(ram_mb, 2)))

    @staticmethod
    def getOsVersion() -> float:
        version_splitted = platform.version().split(".")
        major_version = version_splitted[0]
        medium_version = version_splitted[1]
        return float(f"{major_version}.{medium_version}")

    @staticmethod
    def getUsername() -> str:
        return getpass.getuser()
