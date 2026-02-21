// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

namespace LibProtodec.Reflection;

public interface ICilCustomAttribute
{
    ICilType Type { get; }

    ICilMethod Constructor { get; }

    bool HasConstructorArguments { get; }

    System.Collections.Generic.IReadOnlyList<object?> ConstructorArgumentValues { get; }
}