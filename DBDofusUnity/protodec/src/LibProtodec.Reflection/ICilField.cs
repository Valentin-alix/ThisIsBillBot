// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

namespace LibProtodec.Reflection;

public interface ICilField : ICilCustomAttributeProvider
{
    string Name { get; }

    ICilType Type { get; }

    object? ConstantValue { get; }

    bool IsLiteral  { get; }
    bool IsPublic   { get; }
    bool IsStatic   { get; }
    bool IsInitOnly { get; }
}