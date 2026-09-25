from pathlib import Path

from DBDofusUnity.proto_mapper_assembly.interfaces.field_category import FieldCategoryEnum
from DBDofusUnity.proto_mapper_assembly.parsers.dump_cs_parser import parse_messages


def test_nested_message_is_not_confused_with_an_enum_in_another_scope(tmp_path: Path) -> None:
    path = tmp_path / "protocol.cs"
    path.write_text(
        """
namespace Protocol
{
    public sealed class SelectionEvent : IMessage<SelectionEvent> // TypeDefIndex: 1
    {
        private object result_; // 0x18
        public Types.Error Error { get; set; }
        public static class Types // TypeDefIndex: 2
        {
            public sealed class Error : IMessage<Error> // TypeDefIndex: 3
            {
            }
        }
    }
    public sealed class OtherEvent : IMessage<OtherEvent> // TypeDefIndex: 4
    {
        private Types.Error error_; // 0x18
        private SelectionEvent.Types.Error details_; // 0x20
        private RepeatedField<SelectionEvent.Types.Error> errors_; // 0x28
        private MapField<Types.Error, SelectionEvent.Types.Error> errorsByCode_; // 0x30
        public Types.Error Error { get; set; }
        public SelectionEvent.Types.Error Details { get; set; }
        public RepeatedField<SelectionEvent.Types.Error> Errors { get; }
        public MapField<Types.Error, SelectionEvent.Types.Error> ErrorsByCode { get; }
        public static class Types // TypeDefIndex: 5
        {
            public enum Error { None = 0, Invalid = 1 }
        }
    }
}
""",
        encoding="utf-8",
    )
    messages = {message.name: message for message in parse_messages(str(path))}
    error = next(field for field in messages["SelectionEvent"].fields if field.property_name == "Error")
    assert error.category == FieldCategoryEnum.MESSAGE
    assert error.enum_value_type is None
    assert error.is_synthetic_oneof_variant
    other = {field.property_name: field for field in messages["OtherEvent"].fields}
    assert other["Error"].category == FieldCategoryEnum.ENUM
    assert other["Error"].enum_value_type == "Error"
    assert other["Details"].category == FieldCategoryEnum.MESSAGE
    assert other["Errors"].enum_value_type is None
    assert other["ErrorsByCode"].enum_key_type == "Error"
    assert other["ErrorsByCode"].enum_value_type is None
