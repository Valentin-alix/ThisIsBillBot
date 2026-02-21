// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using LibCpp2IL.Metadata;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppMetadataBackedAttribute(Il2CppAssemblyLoader loader, Il2CppCustomAttributeMetadata attributeMetadata, int metadataIndex) : ICilCustomAttribute
{
    [field: MaybeNull]
    private Il2CppMethodDefinition CtorDef =>
        field ??= loader.Metadata.methodDefs[
            attributeMetadata.ConstructorIndices[metadataIndex]];

    [field: MaybeNull]
    public ICilType Type =>
        field ??= loader.GetType(
            loader.Metadata.GetTypeDefinitionFromIndex(
                CtorDef.declaringTypeIdx));

    [field: MaybeNull]
    public ICilMethod Constructor =>
        field ??= new Il2CppMethod(loader, CtorDef);

    public bool HasConstructorArguments =>
        CtorDef.parameterCount > 0;

    public IReadOnlyList<object?> ConstructorArgumentValues =>
        attributeMetadata.ConstructorArgumentValues[metadataIndex];
}