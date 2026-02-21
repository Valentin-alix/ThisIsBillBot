// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Reflection.PortableExecutable;

namespace LibProtodec.Reflection.Clr;

public sealed class DirectoryAssemblyContainer : AssemblyContainer
{
    private readonly Dictionary<string, string> _assemblyPathLookup = new(StringComparer.OrdinalIgnoreCase);

    public DirectoryAssemblyContainer(string assemblyDir)
    {
        foreach (string assemblyPath in Directory.EnumerateFiles(assemblyDir)
                                                 .Where(static path => path.EndsWith(".dll",       StringComparison.OrdinalIgnoreCase)
                                                                    || path.EndsWith(".exe",       StringComparison.OrdinalIgnoreCase)
                                                                    || path.EndsWith(".dll.bytes", StringComparison.OrdinalIgnoreCase)))
        {
            using FileStream stream = File.OpenRead(assemblyPath);
            using PEReader   reader = new(stream, PEStreamOptions.Default);

            if (!reader.HasMetadata)
                continue;

            _assemblyPathLookup.Add(
                GetAssemblyNameFromPath(assemblyPath),
                assemblyPath);
        }
    }

    public override IReadOnlyCollection<string> GetAssemblyNames() =>
        _assemblyPathLookup.Keys;

    /// <remarks>
    ///     The file name is expected to be the same as the assembly's simple name (casing ignored).
    ///     PublicKeyToken, Version and CultureName are ignored.
    /// </remarks>
    public override Assembly? Resolve(MetadataLoadContext mlc, AssemblyName assemblyName) =>
        _assemblyPathLookup.TryGetValue(assemblyName.Name!, out string? assemblyPath)
            ? mlc.LoadFromAssemblyPath(assemblyPath)
            : null;

    public static string GetAssemblyNameFromPath(string path)
    {
        ReadOnlySpan<char> fileName = Path.GetFileName(path.AsSpan());

        if (fileName.EndsWith(".bytes", StringComparison.OrdinalIgnoreCase))
        {
            fileName = fileName[..^6];
        }

        if (fileName.EndsWith(".dll", StringComparison.OrdinalIgnoreCase)
         || fileName.EndsWith(".exe", StringComparison.OrdinalIgnoreCase))
        {
            fileName = fileName[..^4];
        }

        return fileName.ToString();
    }
}