// Copyright © 2025-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Linq;

namespace LibProtodec.Reflection.Clr;

public abstract class ClrAssemblyLoader : ICilAssemblyLoader
{
    protected readonly Dictionary<string, ClrType> TypeCache = [];

    public IReadOnlyList<ICilType> EnumerateTypes() =>
        TypeCache.Values.ToArray();

    public ICilType GetType(string typeFullName, string assemblySimpleName)
    {
        if (TypeCache.TryGetValue(typeFullName, out ClrType? cachedType))
            return cachedType;

        Type clrType = LoadType(assemblySimpleName, typeFullName);

        return TypeCache[typeFullName] = new ClrType(this, clrType);
    }

    internal ICilType GetType(Type clrType)
    {
        string key = clrType.FullName ?? clrType.Name;

        if (TypeCache.TryGetValue(key, out ClrType? cachedType))
            return cachedType;

        return TypeCache[key] = new ClrType(this, clrType);
    }

    protected abstract Type LoadType(string assemblySimpleName, string typeFullName);
}