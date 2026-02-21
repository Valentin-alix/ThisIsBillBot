// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Reflection;
using CommunityToolkit.Diagnostics;

namespace LibProtodec.Reflection.Clr;

public sealed class ClrMethod(ClrAssemblyLoader loader, MethodBase clrMethod) : ClrMember(loader, clrMethod), ICilMethod
{
    public bool IsConstructor =>
        clrMethod.IsConstructor;

    public bool IsPublic =>
        clrMethod.IsPublic;

    public bool IsStatic =>
        clrMethod.IsStatic;

    public bool IsVirtual =>
        clrMethod.IsVirtual;

    public ICilType ReturnType =>
        this.Loader.GetType(
            clrMethod switch
            {
                MethodInfo methodInfo => methodInfo.ReturnType,
                _ => ThrowHelper.ThrowNotSupportedException<Type>()
            });

    public IEnumerable<ICilType> GetParameterTypes()
    {
        foreach (ParameterInfo parameter in clrMethod.GetParameters())
        {
            yield return this.Loader.GetType(
                parameter.ParameterType);
        }
    }
}