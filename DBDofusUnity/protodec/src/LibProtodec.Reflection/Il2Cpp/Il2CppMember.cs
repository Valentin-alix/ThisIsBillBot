// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using LibCpp2IL;
using LibCpp2IL.Metadata;

namespace LibProtodec.Reflection.Il2Cpp;

public abstract class Il2CppMember(Il2CppAssemblyLoader loader) : ICilCustomAttributeProvider
{
    protected readonly Il2CppAssemblyLoader Loader = loader;
    private ICilCustomAttribute[]? _customAttributes;

    public IReadOnlyList<ICilCustomAttribute> CustomAttributes
    {
        get
        {
            if (_customAttributes is not null)
                return _customAttributes;

            Il2CppImageDefinition declaringAssembly = GetDeclaringAssembly();

            if (Loader.Metadata.MetadataVersion < 29f)
            {
                int attrTypeRngIdx = Loader.Metadata.MetadataVersion <= 24f
                    ? CustomAttributeIndex
                    : BinarySearchToken(
                        Loader.Metadata.attributeTypeRanges!,
                        declaringAssembly.customAttributeStart,
                        (int)declaringAssembly.customAttributeCount,
                        Token);

                if (attrTypeRngIdx < 0)
                    return _customAttributes = [];

                Il2CppCustomAttributeGenerator attributeGenerator = new(Loader, declaringAssembly, attrTypeRngIdx);

                _customAttributes = new ICilCustomAttribute[attributeGenerator.AttributeTypeRange.count];
                for (int i = 0; i < attributeGenerator.AttributeTypeRange.count; i++)
                    _customAttributes[i] = new Il2CppGeneratorBackedAttribute(Loader, attributeGenerator, i);
            }
            else
            {
                int attrDataRngIdx = BinarySearchToken(
                    Loader.Metadata.AttributeDataRanges!,
                    declaringAssembly.customAttributeStart,
                    (int)declaringAssembly.customAttributeCount,
                    Token);

                if (attrDataRngIdx < 0)
                    return _customAttributes = [];

                Il2CppCustomAttributeMetadata attributeMetadata = new(Loader, attrDataRngIdx);

                _customAttributes = new ICilCustomAttribute[attributeMetadata.AttributeCount];
                for (int i = 0; i < attributeMetadata.AttributeCount; i++)
                    _customAttributes[i] = new Il2CppMetadataBackedAttribute(Loader, attributeMetadata, i);
            }

            return _customAttributes;
        }
    }

    protected abstract Il2CppImageDefinition GetDeclaringAssembly();

    protected abstract int CustomAttributeIndex { get; }

    protected abstract uint Token { get; }

    private static int BinarySearchToken<T>(List<T> source, int start, int count, uint targetToken)
        where T : IIl2CppTokenProvider
    {
        int lo = start;
        int hi = start + count - 1;

        while (lo <= hi)
        {
            int i = (lo + hi) >>> 1;
            uint token = source[i].Token;

            if (token == targetToken)
                return i;

            if (token < targetToken)
                lo = i + 1;
            else
                hi = i - 1;
        }

        return ~lo;
    }
}