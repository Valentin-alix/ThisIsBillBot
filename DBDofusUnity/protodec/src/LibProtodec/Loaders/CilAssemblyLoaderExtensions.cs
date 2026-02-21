// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Linq;
using LibProtodec.Reflection;

namespace LibProtodec.Loaders;

public static class CilAssemblyLoaderExtensions
{
    public static IEnumerable<ICilType> GetProtobufMessageTypes(this ICilAssemblyLoader loader)
    {
        ICilType iMessage = loader.GetType("Google.Protobuf.IMessage", "Google.Protobuf");

        return loader.EnumerateTypes().Where(
            type => type is { IsNested: false, IsSealed: true }
                 && type.Namespace?.AsSpan().StartsWith("Google.Protobuf") != true
                 && type.IsAssignableTo(iMessage));
    }

    public static IEnumerable<ICilType> GetProtobufServiceClientTypes(this ICilAssemblyLoader loader)
    {
        ICilType clientBase = loader.GetType("Grpc.Core.ClientBase", "Grpc.Core.Api");

        return loader.EnumerateTypes().Where(
            type => type is { IsNested: true, IsAbstract: false }
                 && type.IsAssignableTo(clientBase));
    }

    public static IEnumerable<ICilType> GetProtobufServiceServerTypes(this ICilAssemblyLoader loader)
    {
        ICilType bindServiceMethodAttribute = loader.GetType("Grpc.Core.BindServiceMethodAttribute", "Grpc.Core.Api");

        return loader.EnumerateTypes().Where(
            type => type is { IsNested: true, IsAbstract: true, DeclaringType: { IsNested: false, IsSealed: true, IsAbstract: true } }
                 && type.CustomAttributes.Any(attribute => attribute.Type == bindServiceMethodAttribute));
    }
}