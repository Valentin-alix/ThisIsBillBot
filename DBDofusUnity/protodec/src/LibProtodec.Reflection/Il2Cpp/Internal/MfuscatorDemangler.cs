// Copyright © 2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Runtime.CompilerServices;
using AssetRipper.Primitives;
using Cpp2IL.Plugin.Mfuscator;

namespace LibProtodec.Reflection.Il2Cpp.Internal;

internal static class MfuscatorDemangler
{
    private static readonly MfuscatorSupportPlugin Plugin = new();

    internal static byte[] DemangleMetadata(byte[] metadata, UnityVersion unityVersion) =>
        Plugin.TryFixupMfuscatorMetadata(metadata, unityVersion)
     ?? throw new Exception("Failed to rebuild metadata");

    [UnsafeAccessor(UnsafeAccessorKind.Method)]
    private static extern byte[]? TryFixupMfuscatorMetadata(
        this MfuscatorSupportPlugin plugin, byte[] originalBytes, UnityVersion unityVersion);
}