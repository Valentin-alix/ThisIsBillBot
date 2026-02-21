// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Reflection;
using System.Runtime.CompilerServices;
using LibCpp2IL;
using LibCpp2IL.Metadata;
using LibCpp2IL.Reflection;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppMethod(Il2CppAssemblyLoader loader, Il2CppMethodDefinition il2CppMethod) : Il2CppMember(loader), ICilMethod
{
    public string Name =>
        il2CppMethod.Name!;

    public bool IsInherited =>
        false;

    public bool IsConstructor =>
        HasAttribute(MethodAttributes.SpecialName)
     && HasAttribute(MethodAttributes.RTSpecialName)
     && (Name == ConstructorInfo.ConstructorName || Name == ConstructorInfo.TypeConstructorName);

    public bool IsPublic =>
        HasAttribute(MethodAttributes.Public);

    public bool IsStatic =>
        HasAttribute(MethodAttributes.Static);

    public bool IsVirtual =>
        HasAttribute(MethodAttributes.Virtual);

    public ICilType ReturnType =>
        this.Loader.GetType(
            LibCpp2ILUtils.GetTypeReflectionData(
                this.Loader.Binary.GetType(
                    il2CppMethod.returnTypeIdx)));

    public IEnumerable<ICilType> GetParameterTypes()
    {
        foreach (Il2CppParameterReflectionData parameter in il2CppMethod.Parameters!)
        {
            yield return this.Loader.GetType(parameter.Type);
        }
    }

    protected override Il2CppImageDefinition GetDeclaringAssembly() =>
        il2CppMethod.DeclaringType!.DeclaringAssembly!;

    protected override int CustomAttributeIndex =>
        il2CppMethod.customAttributeIndex;

    protected override uint Token =>
        il2CppMethod.token;

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    private bool HasAttribute(MethodAttributes attribute) =>
        (il2CppMethod.Attributes & attribute) == attribute;
}