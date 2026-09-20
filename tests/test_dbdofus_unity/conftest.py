from tests.fixtures.proto_mapper.ida_environment import install_mock_ida_environment
from tests.fixtures.pytest_proto_mapper import dump_cs, runtime_data_store

__all__ = ("dump_cs", "runtime_data_store")

install_mock_ida_environment()
