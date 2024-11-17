from pydantic import BaseModel


class VerifiedMapping(BaseModel):
    verified_msg_by_obf: dict[str, str]
    field_mappings: dict[str, dict[str, str]]

    @property
    def verified_msg_by_clear(self) -> dict[str, str]:
        """Returns a dict mapping clear message names to obfuscated names"""
        return {v: k for k, v in self.verified_msg_by_obf.items()}
