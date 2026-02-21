// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;

namespace LibProtodec.Reflection;

public interface ICilType : ICilTypeNameProvider, ICilCustomAttributeProvider
{
    string    DeclaringAssemblyName { get; }
    ICilType? DeclaringType         { get; }
    ICilType? BaseType              { get; }

    [MemberNotNullWhen(true, nameof(DeclaringType))]
    bool IsNested   { get; }
    bool IsAbstract { get; }
    bool IsClass    { get; }
    bool IsEnum     { get; }
    bool IsSealed   { get; }

    IReadOnlyList<ICilType> GenericTypeArguments { get; }

    IEnumerable<ICilField> GetFields();

    IEnumerable<ICilMethod> GetMethods();

    IEnumerable<ICilType> GetNestedTypes();

    IEnumerable<ICilProperty> GetProperties();

    bool IsAssignableTo(ICilType type);
}