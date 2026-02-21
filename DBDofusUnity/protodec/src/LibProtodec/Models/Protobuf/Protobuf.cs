// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.IO;
using System.Linq;
using LibProtodec.Models.Protobuf.TopLevels;

namespace LibProtodec.Models.Protobuf;

public sealed class Protobuf
{
    private HashSet<string>? _wktImports;
    private HashSet<string>? _imports;

    public readonly List<TopLevel> TopLevels = [];

    public string? Edition      { get; set;  }
    public string? AssemblyName { get; init; }
    public string? Namespace    { get; init; }

    [field: MaybeNull]
    public string FileName =>
        field ??= $"{string.Join('_', TopLevels.Select(static topLevel => topLevel.Name))}.proto";

    public HashSet<string> WellKnownImports =>
        _wktImports ??= [];

    public HashSet<string> Imports =>
        _imports ??= [];

    public void WriteTo(IndentedTextWriter writer)
    {
        writer.WriteLine("// Decompiled with protodec");

        if (AssemblyName is not null)
        {
            writer.Write("// Assembly: ");
            writer.WriteLine(AssemblyName);
        }

        writer.WriteLine();
        writer.WriteLine(
            Edition is null
                ? """syntax = "proto3";"""
                : $"""edition = "{Edition}";""");

        if (_wktImports is not null || _imports is not null)
        {
            writer.WriteLine();

            if (_wktImports is not null)
                foreach (string import in _wktImports)
                    WriteImportTo(writer, import);

            if (_imports is not null)
                foreach (string import in _imports)
                    WriteImportTo(writer, import);
        }

        if (Namespace is not null)
        {
            writer.WriteLine();
            WriteOptionTo(writer, "csharp_namespace", Namespace, true);
        }

        foreach (TopLevel topLevel in TopLevels)
        {
            writer.WriteLine();
            topLevel.WriteTo(writer);
        }
    }

    public static void WriteOptionTo(TextWriter writer, string name, string value, bool quoteValue = false)
    {
        writer.Write("option ");
        writer.Write(name);
        writer.Write(" = ");

        if (quoteValue)
        {
            writer.Write('\"');
        }

        writer.Write(value);

        if (quoteValue)
        {
            writer.Write('\"');
        }

        writer.WriteLine(';');
    }

    public static void WriteImportTo(TextWriter writer, string import)
    {
        writer.Write("import \"");
        writer.Write(import);
        writer.WriteLine("\";");
    }
}