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
using SingleFileExtractor.Core;

namespace LibProtodec.Reflection.Clr;

public sealed class BundleAssemblyContainer(Bundle bundle) : AssemblyContainer
{
    private readonly Dictionary<string, FileEntry> _assemblyFileLookup =
        bundle.Files
              .Where(static file => file.Type == FileType.Assembly)
              .ToDictionary(
                   static file => Path.GetFileNameWithoutExtension(file.RelativePath),
                   StringComparer.OrdinalIgnoreCase);

    public override IReadOnlyCollection<string> GetAssemblyNames() =>
        _assemblyFileLookup.Keys;

    /// <remarks>
    ///     The file name is expected to be the same as the assembly's simple name (casing ignored).
    ///     PublicKeyToken, Version and CultureName are ignored.
    /// </remarks>
    public override Assembly? Resolve(MetadataLoadContext mlc, AssemblyName assemblyName) =>
        _assemblyFileLookup.TryGetValue(assemblyName.Name!, out FileEntry? assemblyFile)
            ? mlc.LoadFromStream(
                assemblyFile.AsStream())
            : null;
}