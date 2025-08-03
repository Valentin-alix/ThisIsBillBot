def global_validator_interactive_element(values_array: list[dict[str, object]]) -> bool:
    element_type_id = 0
    element_id = 0
    for values in values_array:
        etype = values["element_type_id"]
        eid = values["element_id"]
        assert isinstance(etype, int)
        assert isinstance(eid, int)
        element_type_id += etype
        element_id += eid
    return element_id >= element_type_id
