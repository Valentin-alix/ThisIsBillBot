// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.IO;
using LibProtodec.Models.Protobuf.TopLevels;
using LibProtodec.Models.Protobuf.Types;

namespace LibProtodec.Models.Protobuf.Fields;

public sealed class MessageField(Message declaringMessage)
{
    public required IProtobufType Type { get; init; }
    public required string        Name { get; init; }

    public bool IsObsolete { get; init; }
    public bool HasHasProp { get; init; }

    public int? Id { get; internal set; }

    public void WriteTo(TextWriter writer, bool isOneOf)
    {
        if (!Id.HasValue)
            writer.Write("// ");

        if (HasHasProp && !isOneOf && Type is not Repeated)
        {
            writer.Write("optional ");
        }

        writer.Write(
            declaringMessage.QualifyTypeName(Type));
        writer.Write(' ');
        writer.Write(Name);
        writer.Write(" = ");

        if (Id.HasValue)
            writer.Write(Id.Value);
        else
            writer.Write('?');

        if (IsObsolete)
        {
            writer.Write(" [deprecated = true]");
        }

        writer.WriteLine(';');
    }
}