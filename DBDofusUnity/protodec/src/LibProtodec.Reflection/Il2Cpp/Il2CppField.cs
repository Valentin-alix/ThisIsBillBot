// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Reflection;
using System.Runtime.CompilerServices;
using LibCpp2IL.Metadata;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppField(Il2CppAssemblyLoader loader, Il2CppFieldDefinition il2CppField) : Il2CppMember(loader), ICilField
{
    private readonly FieldAttributes _attributes =
        (FieldAttributes)il2CppField.RawFieldType!.Attrs;

    public string Name =>
        il2CppField.Name!;

    public ICilType Type =>
        this.Loader.GetType(il2CppField.FieldType!);

    public object? ConstantValue =>
        il2CppField.DefaultValue!.Value;

    public bool IsLiteral =>
        HasAttribute(FieldAttributes.Literal);

    public bool IsPublic =>
        HasAttribute(FieldAttributes.Public);

    public bool IsStatic =>
        HasAttribute(FieldAttributes.Static);

    public bool IsInitOnly =>
        HasAttribute(FieldAttributes.InitOnly);

    protected override Il2CppImageDefinition GetDeclaringAssembly() =>
        il2CppField.FieldType!.baseType!.DeclaringAssembly!;

    protected override int CustomAttributeIndex =>
        il2CppField.customAttributeIndex;

    protected override uint Token =>
        il2CppField.token;

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    private bool HasAttribute(FieldAttributes attribute)
        => (_attributes & attribute) == attribute;
}