// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Diagnostics.CodeAnalysis;

namespace LibProtodec.Reflection;

public struct CilTypeName(string fullName) : ICilTypeNameProvider
{
    private readonly int _lastPlus = fullName.LastIndexOf('+');
    private readonly int _lastDot  = fullName.LastIndexOf('.');

    public string FullName =>
        fullName;

    [field: MaybeNull]
    public string Name =>
        field ??= _lastPlus == -1
            ? _lastDot == -1
                ? FullName
                : FullName.Substring(_lastDot + 1)
            : FullName.Substring(_lastPlus + 1);

    public string? Namespace =>
        _lastDot == -1
            ? null
            : field ??= FullName[.._lastDot];
}