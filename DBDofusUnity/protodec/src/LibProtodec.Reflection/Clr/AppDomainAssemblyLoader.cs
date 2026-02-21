// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using Microsoft.Extensions.Logging;

namespace LibProtodec.Reflection.Clr;

[RequiresDynamicCode(""), RequiresUnreferencedCode("")]
public sealed class AppDomainAssemblyLoader : ClrAssemblyLoader
{
    public AppDomainAssemblyLoader(ILogger? logger = null)
    {
        Assembly[] assemblies = AppDomain.CurrentDomain.GetAssemblies();
        foreach (Assembly assembly in assemblies)
            foreach (Type type in assembly.GetTypes())
                this.TypeCache[type.FullName ?? type.Name] = new ClrType(this, type);

        logger?.LogLoadedTypeAndAssemblyCount(this.TypeCache.Count, assemblies.Length);
    }

    protected override Type LoadType(string assemblySimpleName, string typeFullName) =>
        Assembly.Load(assemblySimpleName).GetType(typeFullName, throwOnError: true)!;
}