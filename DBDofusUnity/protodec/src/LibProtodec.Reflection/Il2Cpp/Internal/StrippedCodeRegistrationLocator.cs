// Copyright © 2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Runtime.CompilerServices;
using Cpp2IL.Plugin.StrippedCodeRegSupport;
using LibCpp2IL;
using LibCpp2IL.BinaryStructures;
using LibCpp2IL.Metadata;

namespace LibProtodec.Reflection.Il2Cpp.Internal;

internal static class StrippedCodeRegistrationLocator
{
    private static readonly StrippedCodeRegSupportPlugin Plugin = new();

    internal static void TryLocate(
        Il2CppBinary                    binary,
        Il2CppMetadata                  metadata,
        ref Il2CppCodeRegistration?     codeReg,
        ref Il2CppMetadataRegistration? metaReg) =>
            Plugin.OnReadFail(binary, metadata, ref codeReg, ref metaReg);

    [UnsafeAccessor(UnsafeAccessorKind.Method)]
    private static extern void OnReadFail(
        this StrippedCodeRegSupportPlugin plugin,
        Il2CppBinary                      binary,
        Il2CppMetadata                    metadata,
        ref Il2CppCodeRegistration?       codeReg,
        ref Il2CppMetadataRegistration?   metaReg);
}