from DBDofusUnity.proto_mapper_assembly.parsers._dump_cs_message_body_parser import parse_message_body


class TestMessageBodyParser:
    def test_assigns_property_names_by_suffix_then_type_fallback(self) -> None:
        stripped_body = """
            private string name_; // 0x18
            private int backing_; // 0x20
            private int unrelated_; // 0x28
            public string Name { get; set; }
            public int Count { get; set; }
            public string Other { get; set; }
        """

        fields, _properties = parse_message_body(stripped_body)
        fields_by_name = {field.field_name: field for field in fields}

        assert fields_by_name["name_"].property_name == "Name"
        assert fields_by_name["backing_"].property_name == "Count"
        assert fields_by_name["unrelated_"].property_name is None

    def test_parses_obfuscated_presence_backing_field_without_field_number_markers(self) -> None:
        stripped_body = """
            private int abc; // 0x18
            private string def; // 0x20
            public string Name { get; set; }
            public bool HasName { get; }
        """

        fields, _properties = parse_message_body(stripped_body)
        fields_by_name = {field.field_name: field for field in fields}

        assert len(_properties) == 1
        assert _properties[0].property_name == "Name"
        assert fields_by_name["abc"].is_proto_field is True
        assert fields_by_name["def"].property_name == "Name"

    def test_marks_obfuscated_presence_backing_field_when_already_mapped(self) -> None:
        stripped_body = """
            private int eqtj; // 0x18
            private int eqtn; // 0x1C
            private readonly RepeatedField<Foo> eqtw; // 0x20
            private int eqtl; // 0x24
            public int foml { get; set; } // 0x0000000100000010-0x0000000100000020 0x0000000100000030-0x0000000100000040
            public RepeatedField<Foo> fomp { get; } // 0x0000000100000050-0x0000000100000060
            public int fomk { get; set; } // 0x0000000100000070-0x0000000100000080 0x0000000100000090-0x00000001000000A0
            public bool fomo { get; }
        """

        fields, _properties = parse_message_body(stripped_body)
        fields_by_name = {field.field_name: field for field in fields}

        assert fields_by_name["eqtj"].is_proto_field is True
        assert fields_by_name["eqtn"].property_name == "fomk"
        assert fields_by_name["eqtw"].property_name == "fomp"
        assert fields_by_name["eqtl"].property_name is None

    def test_marks_premapped_hasbits_when_complete_mapping_has_extra_int_field(self) -> None:
        stripped_body = """
            private int erpw; // 0x18
            public const int erpx = 1;
            private int erpy; // 0x1C
            public const int erpz = 2;
            private static readonly int erqa;
            private int erqb; // 0x20
            public const int erqc = 3;
            private int erqd; // 0x24
            public const int erqe = 4;
            private int erqf; // 0x28
            public int fppc { get; set; }
            public int fppd { get; set; }
            public bool fppe { get; }
            public int fppf { get; set; }
            public int fppg { get; set; }
        """

        fields, _properties = parse_message_body(stripped_body)
        fields_by_name = {field.field_name: field for field in fields}

        assert fields_by_name["erpw"].is_proto_field is False
        assert fields_by_name["erpy"].property_name == "fppc"
        assert fields_by_name["erqb"].property_name == "fppd"
        assert fields_by_name["erqd"].property_name == "fppf"
        assert fields_by_name["erqf"].property_name == "fppg"

    def test_parses_kmv_kmu_kmt_map_field_without_shifted_properties(self) -> None:
        stripped_body = """
            private static readonly MessageParser<kmt> eqsx;
            private UnknownFieldSet eqsy; // 0x10
            private int eqsz; // 0x18
            private int eqtg; // 0x1C
            private int gfak; // 0x20
            private static readonly MapField<int, string> gfam;
            private readonly MapField<int, string> gfan; // 0x28
            private int eqte; // 0x30
            private static readonly int eqtb;
            private int eqtc; // 0x34
            public int fomg { get; set; }
            public int givg { get; set; }
            public MapField<int, string> givh { get; }
            public int fomf { get; set; }
            public int fomd { get; set; }
            public bool fome { get; }
        """

        fields, properties = parse_message_body(stripped_body)
        fields_by_name = {field.field_name: field for field in fields}
        properties_by_name = {property_entry.property_name: property_entry for property_entry in properties}

        assert "givh" in properties_by_name
        assert fields_by_name["eqsz"].is_proto_field is True
        assert fields_by_name["eqtg"].property_name == "givg"
        assert fields_by_name["gfak"].property_name == "fomf"
        assert fields_by_name["gfan"].property_name == "givh"
        assert fields_by_name["eqte"].property_name == "fomd"
        assert fields_by_name["eqtc"].property_name is None

    def test_maps_string_field_after_hasbits_and_before_oneof(self) -> None:
        stripped_body = """
            private int eopd; // 0x18
            public const int eopg = 1;
            private int eopi; // 0x1C
            public const int eope = 2;
            private string eopf; // 0x20
            public const int eopn = 3;
            public const int eopo = 4;
            public const int eopm = 5;
            private object eopp; // 0x28
            private VariantCase eopq; // 0x30
            public int fndt { get; set; } // 0x100-0x200 0x300-0x400
            public string fnds { get; set; } // 0x500-0x600 0x700-0x800
            public FooMsg fndx { get; set; } // 0x900-0xA00 0xB00-0xC00
            public BarMsg fndy { get; set; } // 0xD00-0xE00 0xF00-0x1000
        """

        fields, _properties = parse_message_body(
            stripped_body,
            enum_names=frozenset({"VariantCase"}),
        )
        fields_by_name = {field.field_name: field for field in fields}

        assert fields_by_name["eopf"].property_name == "fnds"
        synthetic_variants = [f for f in fields if f.is_synthetic_oneof_variant]
        synthetic_names = {f.field_name for f in synthetic_variants}
        assert "fnds" not in synthetic_names
        assert "fndx" in synthetic_names
        assert "fndy" in synthetic_names
        for variant in synthetic_variants:
            assert variant.memory_offset == 40

    def test_builds_synthetic_oneof_fields(self) -> None:
        stripped_body = """
            private object content_; // 0x18
            private ContentOneofCase contentCase_; // 0x20
            public Request Request { get; set; }
            public Response Response { get; set; }
        """

        fields, _properties = parse_message_body(
            stripped_body,
            enum_names=frozenset({"ContentOneofCase"}),
        )
        variants_by_name = {field.field_name: field for field in fields if field.is_synthetic_oneof_variant}

        assert set(variants_by_name) == {"Request", "Response"}
        assert variants_by_name["Request"].oneof_group_name == "content"
        assert variants_by_name["Request"].proto_decl_order == 10_000
        assert variants_by_name["Response"].oneof_group_name == "content"
        assert variants_by_name["Response"].proto_decl_order == 10_001

    def test_builds_synthetic_oneof_fields_for_multiple_groups(self) -> None:
        stripped_body = """
            private object content_; // 0x18
            private ContentOneofCase contentCase_; // 0x20
            public Request Request { get; set; }
            public Response Response { get; set; }
            private object result_; // 0x28
            private ResultOneofCase resultCase_; // 0x30
            public Success Success { get; set; }
            public Failure Failure { get; set; }
        """

        fields, _properties = parse_message_body(
            stripped_body,
            enum_names=frozenset({"ContentOneofCase", "ResultOneofCase"}),
        )
        variants_by_name = {field.field_name: field for field in fields if field.is_synthetic_oneof_variant}

        assert set(variants_by_name) == {"Request", "Response", "Success", "Failure"}
        assert variants_by_name["Request"].oneof_group_name == "content"
        assert variants_by_name["Response"].oneof_group_name == "content"
        assert variants_by_name["Success"].oneof_group_name == "result"
        assert variants_by_name["Failure"].oneof_group_name == "result"
        assert variants_by_name["Request"].proto_decl_order == 10_000
        assert variants_by_name["Response"].proto_decl_order == 10_001
        assert variants_by_name["Success"].proto_decl_order == 10_000
        assert variants_by_name["Failure"].proto_decl_order == 10_001

    def test_orders_synthetic_oneof_variants_by_property_position(self) -> None:
        stripped_body = """
            private object content_; // 0x18
            private ContentOneofCase contentCase_; // 0x20
            public Response Response { get; set; }
            public Event Event { get; set; }
            public Request Request { get; set; }
        """

        fields, _properties = parse_message_body(
            stripped_body,
            enum_names=frozenset({"ContentOneofCase"}),
        )
        variants_by_name = {field.field_name: field for field in fields if field.is_synthetic_oneof_variant}

        assert list(variants_by_name) == ["Response", "Event", "Request"]
        assert variants_by_name["Response"].proto_decl_order == 10_000
        assert variants_by_name["Event"].proto_decl_order == 10_001
        assert variants_by_name["Request"].proto_decl_order == 10_002
