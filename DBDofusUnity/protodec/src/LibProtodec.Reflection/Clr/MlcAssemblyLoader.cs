// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.IO;
using System.Linq;
using System.Reflection;
using Microsoft.Extensions.Logging;
using SingleFileExtractor.Core;

namespace LibProtodec.Reflection.Clr;

[UnconditionalSuppressMessage("AssemblyLoadTrimming", "IL2026", Justification = $"Irrelevant to assemblies loaded via {nameof(MetadataLoadContext)}.")]
public sealed class MlcAssemblyLoader : ClrAssemblyLoader, IDisposable
{
    public readonly AssemblyContainer   AssemblyContainer;
    public readonly MetadataLoadContext LoadContext;
    public readonly ExecutableReader?   BundleReader;

    public MlcAssemblyLoader(string targetPath, string? targetAssemblyName = null, ILogger? logger = null)
    {
        targetPath = Path.GetFullPath(targetPath);

        if (File.Exists(targetPath))
        {
            ExecutableReader bundleReader = new(targetPath);

            if (bundleReader is { IsSupported: true, IsSingleFile: true })
            {
                BundleReader      = bundleReader;
                AssemblyContainer = new BundleAssemblyContainer(bundleReader.Bundle);
            }
            else
            {
                bundleReader.Dispose();

                AssemblyContainer = new DirectoryAssemblyContainer(
                    Path.GetDirectoryName(targetPath)!);

                targetAssemblyName ??= DirectoryAssemblyContainer.GetAssemblyNameFromPath(targetPath);
            }
        }
        else
        {
            AssemblyContainer = new DirectoryAssemblyContainer(targetPath);
        }

        LoadContext = new MetadataLoadContext(AssemblyContainer);

        LoadTypes(targetAssemblyName, logger);
    }

    public MlcAssemblyLoader(AssemblyContainer container, string? targetAssemblyName = null, ILogger? logger = null)
    {
        AssemblyContainer = container;
        LoadContext       = new MetadataLoadContext(container);

        LoadTypes(targetAssemblyName, logger);
    }

    private void LoadTypes(string? targetAssemblyName = null, ILogger? logger = null)
    {
        IEnumerable<Type> allTypes = targetAssemblyName is null
            ? AssemblyContainer.GetAssemblyNames().SelectMany(name => LoadContext.LoadFromAssemblyName(name).GetTypes())
            : LoadContext.LoadFromAssemblyName(targetAssemblyName).GetTypes();

        foreach (Type type in allTypes)
            this.TypeCache[type.FullName ?? type.Name] = new ClrType(this, type);

        logger?.LogLoadedTypeAndAssemblyCount(this.TypeCache.Count, LoadContext.GetAssemblies().Count());
    }

    protected override Type LoadType(string assemblySimpleName, string typeFullName) =>
        LoadContext.LoadFromAssemblyName(assemblySimpleName)
                   .GetType(typeFullName, throwOnError: true)!;

    public void Dispose()
    {
        LoadContext.Dispose();
        BundleReader?.Dispose();
    }
}