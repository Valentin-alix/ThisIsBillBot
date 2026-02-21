// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using CommunityToolkit.Diagnostics;
using LibCpp2IL;
using LibCpp2IL.Metadata;
using LibCpp2IL.Reflection;

namespace LibProtodec.Reflection.Il2Cpp;

[DebuggerDisplay("{FullName,nq}")]
public sealed class Il2CppType : Il2CppMember, ICilType
{
    private readonly Il2CppTypeDefinition _il2CppType;
    private readonly Il2CppTypeReflectionData[] _genericArgs;
    private ICilType[]? _genericTypeArguments;

    internal Il2CppType(Il2CppAssemblyLoader loader, Il2CppTypeDefinition il2CppType, Il2CppTypeReflectionData[] genericArgs) : base(loader) =>
        (_il2CppType, _genericArgs) = (il2CppType, genericArgs);

    public string Name =>
        _il2CppType.Name!;

    public string FullName =>
        _il2CppType.FullName!;

    public string? Namespace =>
        _il2CppType.Namespace;

    public string DeclaringAssemblyName =>
        this.Loader.Metadata.GetStringFromIndex(
            GetDeclaringAssembly().nameIndex);

    public ICilType? DeclaringType =>
        IsNested
            ? this.Loader.GetType(
                LibCpp2ILUtils.GetTypeReflectionData(
                    this.Loader.Binary.GetType(
                        _il2CppType.DeclaringTypeIndex)))
            : null;

    public ICilType? BaseType =>
        _il2CppType.ParentIndex.Value == -1
            ? null
            : this.Loader.GetType(
                LibCpp2ILUtils.GetTypeReflectionData(
                    this.Loader.Binary.GetType(
                        _il2CppType.ParentIndex)));

    public bool IsAbstract =>
        _il2CppType.IsAbstract;

    public bool IsClass =>
        (_il2CppType.Attributes & TypeAttributes.ClassSemanticsMask) == TypeAttributes.Class
     && !_il2CppType.IsValueType;

    public bool IsEnum =>
        _il2CppType.IsEnumType;

    [MemberNotNullWhen(true, nameof(DeclaringType))]
    public bool IsNested =>
        _il2CppType.DeclaringTypeIndex.Value >= 0;

    public bool IsSealed =>
        (_il2CppType.Attributes & TypeAttributes.Sealed) == TypeAttributes.Sealed;

    public IReadOnlyList<ICilType> GenericTypeArguments
    {
        get
        {
            if (_genericTypeArguments is null)
            {
                if (_genericArgs.Length < 1)
                {
                    return _genericTypeArguments = [];
                }

                _genericTypeArguments = new ICilType[_genericArgs.Length];

                for (int i = 0; i < _genericArgs.Length; i++)
                {
                    _genericTypeArguments[i] = this.Loader.GetType(_genericArgs[i]);
                }
            }

            return _genericTypeArguments;
        }
    }

    public IEnumerable<ICilField> GetFields()
    {
        for (ushort i = 0; i < _il2CppType.FieldCount; i++)
        {
            yield return new Il2CppField(
                this.Loader,
                this.Loader.Metadata.GetFieldDefinitionFromOffset(_il2CppType.FirstFieldIdx, i));
        }
    }

    public IEnumerable<ICilMethod> GetMethods()
    {
        for (ushort i = 0; i < _il2CppType.MethodCount; i++)
        {
            yield return new Il2CppMethod(
                this.Loader,
                this.Loader.Metadata.GetMethodDefinitionFromOffset(_il2CppType.FirstMethodIdx, i));
        }
    }

    public IEnumerable<ICilType> GetNestedTypes()
    {
        for (ushort i = 0; i < _il2CppType.NestedTypeCount; i++)
        {
            yield return this.Loader.GetType(
                this.Loader.Metadata.GetTypeDefinitionFromIndex(
                    Il2CppVariableWidthIndex<Il2CppTypeDefinition>.MakeTemporaryForFixedWidthUsage(
                        this.Loader.Metadata.GetNestedTypeIndicesFromOffset(_il2CppType.NestedTypesStart, i).Value)));
        }
    }

    public IEnumerable<ICilProperty> GetProperties()
    {
        for (ushort i = 0; i < _il2CppType.PropertyCount; i++)
        {
            yield return new Il2CppProperty(
                this.Loader,
                this.Loader.Metadata.GetPropertyDefinitionsFromOffset(_il2CppType.FirstPropertyId, i),
                _il2CppType);
        }
    }

    public bool IsAssignableTo(ICilType type)
    {
        if (type is Il2CppType il2CppType)
        {
            return IsAssignableTo(_il2CppType, il2CppType._il2CppType);
        }

        return ThrowHelper.ThrowNotSupportedException<bool>();
    }

    protected override Il2CppImageDefinition GetDeclaringAssembly() =>
        _il2CppType.DeclaringAssembly!;

    protected override int CustomAttributeIndex =>
        _il2CppType.CustomAttributeIndex;

    protected override uint Token =>
        _il2CppType.Token;

    private bool IsAssignableTo(Il2CppTypeDefinition thisType, Il2CppTypeDefinition baseType)
    {
        if (baseType.IsInterface)
        {
            for (ushort i = 0; i < _il2CppType.InterfacesCount; i++)
            {
                Il2CppTypeReflectionData interfaceType = LibCpp2ILUtils.GetTypeReflectionData(
                    this.Loader.Binary.GetType(
                        this.Loader.Metadata.GetInterfaceIndicesFromOffset(_il2CppType.InterfacesStart, i)));

                if (interfaceType.baseType == baseType)
                {
                    return true;
                }
            }
        }
        
        if (thisType == baseType)
        {
            return true;
        }

        Il2CppTypeDefinition? thisTypeBaseType = thisType.BaseType?.baseType;

        return thisTypeBaseType is not null
            && IsAssignableTo(thisTypeBaseType, baseType);
    }
}