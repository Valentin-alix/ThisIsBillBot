// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Linq;
using System.Reflection;
using CommunityToolkit.Diagnostics;
using LibCpp2IL.Metadata;
using Il2CppTypeStruct = LibCpp2IL.BinaryStructures.Il2CppType;
using VariableWidthIndex = LibCpp2IL.Metadata.Il2CppVariableWidthIndex<LibCpp2IL.BinaryStructures.Il2CppType>;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppGeneratorBackedAttribute(Il2CppAssemblyLoader loader, Il2CppCustomAttributeGenerator generator, int index) : ICilCustomAttribute
{
    public readonly Il2CppCustomAttributeGenerator Generator = generator;
    public readonly int Index = index;

    [field: MaybeNull]
    private Il2CppTypeDefinition TypeDef
    {
        get
        {
            if (field is null)
            {
                VariableWidthIndex typeIndex = VariableWidthIndex.MakeTemporaryForFixedWidthUsage(
                    loader.Metadata.attributeTypes![Generator.AttributeTypeRange.start + Index]);

                Il2CppTypeStruct type = loader.Binary.GetType(typeIndex);

                field = loader.Metadata.GetTypeDefinitionFromIndex(type.Data.ClassIndex);
            }

            return field;
        }
    }

    [field: MaybeNull]
    private Il2CppMethodDefinition CtorDef =>
        field ??= TypeDef.Methods!.First(static method =>
            method.Name == ConstructorInfo.ConstructorName);

    [field: MaybeNull]
    public ICilType Type =>
        field ??= loader.GetType(TypeDef);

    [field: MaybeNull]
    public ICilMethod Constructor =>
        field ??= new Il2CppMethod(loader, CtorDef);

    public bool HasConstructorArguments =>
        CtorDef.parameterCount > 0;

    public IReadOnlyList<object?> ConstructorArgumentValues =>
        HasConstructorArguments
            ? ThrowHelper.ThrowNotSupportedException<IReadOnlyList<object?>>(
                  "Attribute constructor argument parsing is only implemented for IL2CPP metadata version 29 or greater.")
            : [];
}