import importlib
import sys
from types import SimpleNamespace
from unittest import TestCase
from unittest.mock import Mock, patch


class TestDevice(TestCase):
    def test_get_cpu_model_on_windows_initializes_com_and_reads_wmi(self) -> None:
        cpu_info = SimpleNamespace(Name="Mock CPU")
        co_initialize = Mock()
        wmi_client = SimpleNamespace(Win32_Processor=lambda: [cpu_info])
        wmi_module = SimpleNamespace(WMI=lambda: wmi_client)
        pythoncom_module = SimpleNamespace(CoInitialize=co_initialize)
        module_name = "AnkamaLauncherEmulatorPremium.ankama_launcher_emulator_premium.decrypter.device"

        with patch.dict(
            sys.modules,
            {
                "pythoncom": pythoncom_module,
                "wmi": wmi_module,
            },
        ):
            sys.modules.pop(module_name, None)
            device_module = importlib.import_module(module_name)
            with (
                patch.object(device_module.psutil, "WINDOWS", True),
                patch.object(device_module.psutil, "LINUX", False),
                patch.object(device_module.psutil, "MACOS", False),
                patch.object(device_module, "wmi", wmi_module),
                patch.object(device_module, "pythoncom", pythoncom_module),
            ):
                cpu_model = device_module.Device.getCpuModel()

        self.assertEqual(cpu_model, "Mock CPU")
        co_initialize.assert_called_once_with()
