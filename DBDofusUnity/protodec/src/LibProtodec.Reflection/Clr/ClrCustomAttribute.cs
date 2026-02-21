// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.Reflection;

namespace LibProtodec.Reflection.Clr;

public sealed class ClrCustomAttribute(ClrAssemblyLoader loader, CustomAttributeData clrAttribute) : ICilCustomAttribute
{
    private object?[]? _constructorArgumentValues;

    [field: MaybeNull]
    public ICilType Type =>
        field ??= loader.GetType(
            clrAttribute.AttributeType);

    [field: MaybeNull]
    public ICilMethod Constructor =>
        field ??= new ClrMethod(loader, clrAttribute.Constructor);

    public bool HasConstructorArguments =>
        clrAttribute.ConstructorArguments.Count > 0;

    public IReadOnlyList<object?> ConstructorArgumentValues
    {
        get
        {
            if (_constructorArgumentValues is null)
            {
                IList<CustomAttributeTypedArgument> args = clrAttribute.ConstructorArguments;
                if (args.Count < 1)
                {
                    return _constructorArgumentValues = [];
                }

                _constructorArgumentValues = new object[args.Count];

                for (int i = 0; i < args.Count; i++)
                {
                    _constructorArgumentValues[i] = args[i].Value;
                }
            }

            return _constructorArgumentValues;
        }
    }
}