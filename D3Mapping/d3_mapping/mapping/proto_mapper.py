from dataclasses import dataclass

from tqdm import tqdm

from D3Mapping.d3_mapping.mapping.comparison_engine import ComparisonEngine
from D3Mapping.d3_mapping.mapping.proto_organization import ProtoOrganization
from D3Mapping.d3_mapping.mapping.validators.field_validators import VALIDATORS_ON_FIELD
from D3Mapping.d3_mapping.mapping.validators.global_validators import (
    VALIDATORS_GLOBAL_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.mapping.validators.proto_field_validators import (
    is_parsed_obf_msg,
)
from D3Mapping.d3_mapping.mapping.validators.set_validators import (
    VALIDATORS_ON_SET_FIELDS,
)
from D3Mapping.d3_mapping.models.mapping_info import (
    MappingInfo,
    OutputFieldMapping,
    OutputMappingInfo,
)
from D3Mapping.d3_mapping.models.p_message import (
    PMessage,
)


@dataclass
class ProtoMapper(ComparisonEngine):
    clear_root_namespaces: list[str]
    obf_root_namespaces: list[str]

    msg_mapping_info_by_obf_namespace: dict[str, OutputMappingInfo]

    def __post_init__(self):
        self.verified_msg_by_clear = {
            value: key for key, value in self.verified_msg_by_obf.items()
        }

    def run_mapping(self) -> dict[str, OutputMappingInfo]:
        sorted_obf_struct_to_map_fields = sorted(
            [
                obf_struct
                for obf_struct in self.obf_struct_by_namespace.values()
                if isinstance(obf_struct, PMessage)
                and obf_struct.namespace in self.verified_msg_by_obf
            ],
            key=lambda obf_struct: max(
                VALIDATORS_ON_SET_FIELDS.get(
                    self.verified_msg_by_obf[obf_struct.namespace], (None, 0)
                )[1],
                VALIDATORS_GLOBAL_ON_SET_FIELDS.get(
                    self.verified_msg_by_obf[obf_struct.namespace], (None, 0)
                )[1],
            ),
            reverse=True,
        )
        for obf_msg in tqdm(sorted_obf_struct_to_map_fields):
            related_clear_msg_name = self.verified_msg_by_obf[obf_msg.namespace]
            related_clear_namespace = next(
                (
                    namespace
                    for namespace in self.clear_struct_by_namespace
                    if namespace.split(".")[-1] == related_clear_msg_name
                ),
                None,
            )
            if related_clear_namespace is None:
                continue

            related_clear_msg = self.clear_struct_by_namespace[related_clear_namespace]
            assert isinstance(related_clear_msg, PMessage)

            mapping_info = self.get_comparison_message(
                related_clear_msg, obf_msg, set()
            )
            self.add_new_msg_mapping(related_clear_msg, obf_msg, mapping_info)

        clear_msg_namespace_treateds = {
            mapping_info.clear_msg_namespace
            for mapping_info in self.msg_mapping_info_by_obf_namespace.values()
        }
        print("searching remaining clear_msgs")
        remaining_clear_msgs = [
            msg
            for namespace in self.clear_root_namespaces
            if namespace not in clear_msg_namespace_treateds
            and isinstance((msg := self.clear_struct_by_namespace[namespace]), PMessage)
            and msg.name in ["GameMessage"]
        ]
        for clear_msg in tqdm(remaining_clear_msgs):
            mapping_info = self.get_most_similar_obf_msg(clear_msg)
            if mapping_info is None:
                continue
            self.add_new_msg_mapping(clear_msg, mapping_info[0], mapping_info[1])

        return self.msg_mapping_info_by_obf_namespace

    def get_most_similar_obf_msg(self, clear_msg: PMessage):
        most_sim_msg_info: tuple[PMessage, MappingInfo] | None = None
        for obf_namespace in tqdm(self.obf_root_namespaces):
            related_obf_struct = self.obf_struct_by_namespace[obf_namespace]
            if not isinstance(related_obf_struct, PMessage):
                continue
            mapping_info = self.get_comparison_message(
                clear_msg, related_obf_struct, set()
            )
            if (
                most_sim_msg_info is None
                or most_sim_msg_info[1].similarity < mapping_info.similarity
            ):
                most_sim_msg_info = (related_obf_struct, mapping_info)

        return most_sim_msg_info

    def add_new_msg_mapping(
        self, clear_msg: PMessage, obf_msg: PMessage, mapping_info: MappingInfo
    ):
        if obf_msg.namespace in self.msg_mapping_info_by_obf_namespace:
            # already matched, skip
            return

        if (
            clear_msg.name in VALIDATORS_ON_FIELD
            or clear_msg.name in VALIDATORS_ON_SET_FIELDS
            or clear_msg.name in VALIDATORS_GLOBAL_ON_SET_FIELDS
        ) and not is_parsed_obf_msg(obf_msg.namespace):
            print(
                f"<!> Not enough registered msg for {clear_msg.name} with obf_msg {obf_msg.name}"
            )

        self._added_mapping_by_obf_namespaces[obf_msg.namespace] = mapping_info

        output_field_mapping: OutputFieldMapping = {}

        for _obf_field_name, _mapping_info in mapping_info.field_mapping.items():
            if _mapping_info is None:
                output_field_mapping[_obf_field_name] = None
                continue
            _field_sim, _clear_field_name, _sub_mapping_info = _mapping_info
            output_field_mapping[_obf_field_name] = _field_sim, _clear_field_name

            if _sub_mapping_info is not None:
                _sub_obf_msg = ProtoOrganization.get_related_struct_from_field_name(
                    self.obf_struct_by_namespace, obf_msg, _obf_field_name
                )
                _sub_clear_msg = self.clear_struct_by_namespace[
                    _sub_mapping_info.clear_msg_namespace
                ]

                assert (
                    type(_sub_obf_msg) is PMessage and type(_sub_clear_msg) is PMessage
                )
                self.add_new_msg_mapping(
                    _sub_clear_msg, _sub_obf_msg, _sub_mapping_info
                )

        self.msg_mapping_info_by_obf_namespace[obf_msg.namespace] = OutputMappingInfo(
            clear_msg_namespace=clear_msg.namespace,
            similarity=mapping_info.similarity,
            field_mapping=output_field_mapping,
        )
