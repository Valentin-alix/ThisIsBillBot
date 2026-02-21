from typing import ClassVar, TypeVar

_SelfT = TypeVar("_SelfT")


class SingletonTypeError(TypeError):
    pass


class Singleton(type):
    _instances: ClassVar[dict[type[object], object]] = {}

    def __call__(cls: type[_SelfT], *args: object, **kwargs: object) -> _SelfT:
        instance = Singleton._instances.get(cls)
        if instance is None:
            instance = super().__call__(*args, **kwargs)
            Singleton._instances[cls] = instance
        if not isinstance(instance, cls):
            raise SingletonTypeError
        return instance
