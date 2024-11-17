import unittest
from unittest.mock import patch

from D3Mapping.d3_mapping.mapping.validators.proto_validator import ProtoValidator


class TestProtoValidatorPerformance(unittest.TestCase):
    def test_validators_cache_works(self):
        validator = ProtoValidator(
            clear_struct_by_namespace={},
            obf_struct_by_namespace={},
            msg_mapping_info_by_obf_namespace={},
        )

        with (
            patch(
                "D3Mapping.d3_mapping.mapping.validators.proto_validator.VALIDATORS_ON_SET_FIELDS",
                {"TestMsg": ("validator_func", 1)},
            ),
            patch(
                "D3Mapping.d3_mapping.mapping.validators.proto_validator.VALIDATORS_GLOBAL_ON_SET_FIELDS",
                {"TestMsg": ("global_validator_func", 1)},
            ),
        ):
            result1 = validator._get_validators("TestMsg")
            result2 = validator._get_validators("TestMsg")
            result3 = validator._get_validators("TestMsg")

            assert result1 is result2 is result3
            assert result1 == (
                ("validator_func", 1),
                ("global_validator_func", 1),
            )


if __name__ == "__main__":
    unittest.main()
