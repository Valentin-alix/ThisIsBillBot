// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;
using CommunityToolkit.Diagnostics;

namespace LibProtodec.Reflection.Clr;

[UnconditionalSuppressMessage("AssemblyLoadTrimming", "IL2080", Justification = $"Irrelevant to assemblies loaded via {nameof(MetadataLoadContext)}.")]
[DebuggerDisplay("{FullName,nq}")]
public sealed class ClrType : ClrMember, ICilType
{
    private const BindingFlags Everything = BindingFlags.NonPublic | BindingFlags.Public | BindingFlags.Static | BindingFlags.Instance;

    private readonly Type _clrType;
    private ICilType[]? _genericTypeArguments;

    internal ClrType(ClrAssemblyLoader loader, Type clrType) : base(loader, clrType) =>
        _clrType = clrType;

    public string FullName =>
        _clrType.FullName ?? _clrType.Name;

    public string? Namespace =>
        _clrType.Namespace;

    public string DeclaringAssemblyName =>
        _clrType.Assembly.FullName!;

    public ICilType? BaseType =>
        _clrType.BaseType is null
            ? null
            : this.Loader.GetType(
                _clrType.BaseType);

    public bool IsAbstract =>
        _clrType.IsAbstract;

    public bool IsClass =>
        _clrType.IsClass;

    public bool IsEnum =>
        _clrType.IsEnum;

    public bool IsNested =>
        _clrType.IsNested;

    public bool IsSealed =>
        _clrType.IsSealed;

    public IReadOnlyList<ICilType> GenericTypeArguments
    {
        get
        {
            if (_genericTypeArguments is null)
            {
                Type[] genericArgs = _clrType.GenericTypeArguments;
                if (genericArgs.Length < 1)
                {
                    return _genericTypeArguments = [];
                }

                _genericTypeArguments = new ICilType[genericArgs.Length];

                for (int i = 0; i < genericArgs.Length; i++)
                {
                    _genericTypeArguments[i] = this.Loader.GetType(genericArgs[i]);
                }
            }

            return _genericTypeArguments;
        }
    }

    public IEnumerable<ICilField> GetFields()
    {
        foreach (FieldInfo field in _clrType.GetFields(Everything))
        {
            yield return new ClrField(this.Loader, field);
        }
    }

    public IEnumerable<ICilMethod> GetMethods()
    {
        foreach (MethodInfo method in _clrType.GetMethods(Everything))
        {
            yield return new ClrMethod(this.Loader, method);
        }
    }

    public IEnumerable<ICilType> GetNestedTypes()
    {
        foreach (Type type in _clrType.GetNestedTypes(Everything))
        {
            yield return this.Loader.GetType(type);
        }
    }

    public IEnumerable<ICilProperty> GetProperties()
    {
        foreach (PropertyInfo property in _clrType.GetProperties(Everything))
        {
            yield return new ClrProperty(this.Loader, property);
        }
    }

    public bool IsAssignableTo(ICilType type)
    {
        if (type is ClrType clrType)
        {
            return _clrType.IsAssignableTo(clrType._clrType);
        }

        return ThrowHelper.ThrowNotSupportedException<bool>();
    }
}