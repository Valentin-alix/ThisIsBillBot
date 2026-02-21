// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using LibCpp2IL.Metadata;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppCustomAttributeGenerator(Il2CppAssemblyLoader loader, Il2CppImageDefinition declaringAssembly, int attrTypeRngIdx)
{
    public readonly Il2CppCustomAttributeTypeRange AttributeTypeRange = loader.Metadata.attributeTypeRanges![attrTypeRngIdx];
    public readonly ulong FunctionAddress = loader.Metadata.MetadataVersion < 27f
        ? loader.Binary.GetCustomAttributeGenerator(attrTypeRngIdx)
        : loader.Binary.ReadPointerAtVirtualAddress(
            loader.Binary.GetCodegenModuleByName(declaringAssembly.Name!)!.customAttributeCacheGenerator
          + unchecked((ulong)(attrTypeRngIdx - declaringAssembly.customAttributeStart)) * loader.Binary.PointerSize);
}