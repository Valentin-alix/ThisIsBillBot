def get_value_with_len_malus(
    value: float, len_clear_elems: int, len_obf_elems: int
) -> float:
    malus = 2 if len_clear_elems > len_obf_elems else 1
    if len_obf_elems - 1 == len_clear_elems:
        return value / 1.1

    min_len_elems = min(len_clear_elems, len_obf_elems)
    max_len_elems = max(len_clear_elems, len_obf_elems)
    return value * (min_len_elems / max_len_elems) / malus
