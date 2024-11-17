from dataclasses import dataclass

from D3Mapping.d3_mapping.models.p_message import PMessage


@dataclass(frozen=True)
class ComparisonContext:
    """Context for message comparison operations.

    This class encapsulates all the parameters needed for comparing
    two protobuf messages, reducing parameter passing complexity.
    """

    clear_msg: PMessage
    obf_msg: PMessage
    treated_namespaces: set[str]

    @property
    def cache_key(self) -> tuple[str, str]:
        """Returns a cache key for this comparison context."""
        return (self.clear_msg.namespace, self.obf_msg.namespace)

    def with_treated(self, namespace: str) -> "ComparisonContext":
        """Returns a new context with an additional treated namespace."""
        new_treated = self.treated_namespaces.copy()
        new_treated.add(namespace)
        return ComparisonContext(
            clear_msg=self.clear_msg,
            obf_msg=self.obf_msg,
            treated_namespaces=new_treated,
        )


@dataclass(frozen=True)
class FieldComparisonContext:
    """Context for field comparison operations."""

    clear_msg: PMessage
    obf_msg: PMessage
    treated_namespaces: set[str]

    @classmethod
    def from_message_context(
        cls, msg_ctx: ComparisonContext
    ) -> "FieldComparisonContext":
        """Create a field context from a message context."""
        return cls(
            clear_msg=msg_ctx.clear_msg,
            obf_msg=msg_ctx.obf_msg,
            treated_namespaces=msg_ctx.treated_namespaces,
        )
