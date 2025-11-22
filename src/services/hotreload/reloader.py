import gc
import importlib
import os
import sys
import threading
from dataclasses import dataclass, field
from types import ModuleType

_CORE_MODULE_PREFIX = "src.core"

_reload_lock = threading.Lock()
_known_mtimes: dict[str, float] = {}


@dataclass
class ReloadReport:
    reloaded_modules: list[str] = field(default_factory=list[str])
    patched_classes: dict[str, int] = field(default_factory=dict[str, int])
    errors: dict[str, str] = field(default_factory=dict[str, str])

    @property
    def patched_instance_count(self) -> int:
        return sum(self.patched_classes.values())


def _core_modules_with_source() -> dict[str, ModuleType]:
    modules: dict[str, ModuleType] = {}
    for name, module in list(sys.modules.items()):
        if not name.startswith(_CORE_MODULE_PREFIX) or module is None:
            continue
        if getattr(module, "__file__", None) is None:
            continue
        modules[name] = module
    return modules


def _classes_defined_in(module: ModuleType) -> dict[str, type]:
    return {
        attr_name: attr
        for attr_name, attr in vars(module).items()
        if isinstance(attr, type) and attr.__module__ == module.__name__
    }


def _patch_live_instances(old_cls: type, new_cls: type) -> int:
    instances = [obj for obj in gc.get_objects() if type(obj) is old_cls]
    for instance in instances:
        instance.__class__ = new_cls
    return len(instances)


def reload_core_modules() -> ReloadReport:
    """Reload changed modules under `src.core` and re-point already-live instances
    (Behaviors, Frames, GameState sub-states, ...) at the new class code, in place.

    Only instances that already exist are patched; other `src.core` modules that did
    `from x import SomeClass` keep referencing the pre-reload class for anything they
    construct afterwards. Adding/removing dataclass fields is not migrated onto
    existing instances - a process restart is still required for those changes.
    """
    report = ReloadReport()
    with _reload_lock:
        for name, module in _core_modules_with_source().items():
            file_path = module.__file__
            assert file_path is not None
            try:
                mtime = os.path.getmtime(file_path)
            except OSError as error:
                report.errors[name] = str(error)
                continue

            last_mtime = _known_mtimes.get(name)
            if last_mtime is None:
                _known_mtimes[name] = mtime
                continue
            if mtime <= last_mtime:
                continue

            old_classes = _classes_defined_in(module)
            try:
                importlib.reload(module)
            except Exception as error:
                report.errors[name] = str(error)
                continue

            _known_mtimes[name] = mtime
            report.reloaded_modules.append(name)

            for class_name, old_cls in old_classes.items():
                new_cls = getattr(module, class_name, None)
                if not isinstance(new_cls, type) or new_cls is old_cls:
                    continue
                patched_count = _patch_live_instances(old_cls, new_cls)
                if patched_count:
                    report.patched_classes[f"{name}.{class_name}"] = patched_count

    return report
