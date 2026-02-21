// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Reflection;

namespace LibProtodec.Reflection.Clr;

public sealed class ClrProperty(ClrAssemblyLoader loader, PropertyInfo clrProperty) : ClrMember(loader, clrProperty), ICilProperty
{
    private readonly MethodInfo? _getterInfo = clrProperty.GetMethod;
    private readonly MethodInfo? _setterInfo = clrProperty.SetMethod;

    private ClrMethod? _getter;
    private ClrMethod? _setter;

    public bool CanRead =>
        _getterInfo is not null;

    public bool CanWrite =>
        _setterInfo is not null;

    public ICilMethod? Getter =>
        _getterInfo is null
            ? null
            : _getter ??= new ClrMethod(this.Loader, _getterInfo);

    public ICilMethod? Setter =>
        _setterInfo is null
            ? null
            : _setter ??= new ClrMethod(this.Loader, _setterInfo);

    public ICilType Type =>
        this.Loader.GetType(
            clrProperty.PropertyType);
}