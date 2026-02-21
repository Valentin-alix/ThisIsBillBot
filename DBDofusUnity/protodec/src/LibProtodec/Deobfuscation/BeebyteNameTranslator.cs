// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.Diagnostics.CodeAnalysis;
using System.IO;
using CommunityToolkit.HighPerformance;
using SystemEx;
using SystemEx.Memory;
using ZLinq;

namespace LibProtodec.Deobfuscation;

public sealed class BeebyteNameTranslator(IReadOnlyDictionary<string, string> nameMap) : INameTranslator
{
    public bool IsNameObfuscated(string name) =>
        (name.Length == 11 && name.CountUpper() == 11)
     || name.AsValueEnumerable().All(static chr => !char.IsAscii(chr));

    public bool TryTranslateMemberName(string obfuscatedName, [MaybeNullWhen(false)] out string translatedName) =>
        nameMap.TryGetValue(obfuscatedName, out translatedName);

    public bool TryTranslateTypeName(string obfuscatedName, [MaybeNullWhen(false)] out string translatedName)
    {
        if (!nameMap.TryGetValue(obfuscatedName, out translatedName))
            return false;

        ReadOnlySpan<char> typeName = translatedName.AsSpan();
        switch (ReadOnlySpanExtensions.Count(typeName, '/'))
        {
            case 0:
                return true;
            case 3:
                typeName = typeName[(typeName.IndexOf('/') + 1)..];
                break;
            case 7:
                for (int i = 0; i < 4; i++)
                    typeName = typeName[(typeName.IndexOf('/') + 1)..];
                break;
        }

        translatedName = StringEx.Allocate(typeName.Length);
        typeName.Replace(translatedName.AsWriteableSpan(), '/', '+');

        return true;
    }

    public static BeebyteNameTranslator FromNameTranslationTxt(string path) =>
        FromNameTranslationTxt(
            File.ReadAllLines(path));

    public static BeebyteNameTranslator FromNameTranslationTxt(IEnumerable<string> lines)
    {
        Dictionary<string, string> nameMap = [];
        foreach (string line in lines)
        {
            if (line.StartsWith('#'))
                continue;

            int sep = line.IndexOf('\u21e8');
            if (sep < 0)
                continue;

            nameMap.Add(line[..sep], line[++sep..]);
        }

        return new BeebyteNameTranslator(nameMap);
    }
}