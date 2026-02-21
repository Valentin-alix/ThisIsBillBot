// Copyright © 2025 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Diagnostics.CodeAnalysis;

namespace LibProtodec.Deobfuscation;

public interface INameTranslator
{
    bool IsNameObfuscated(string name);

    bool TryTranslateMemberName(string obfuscatedName, [MaybeNullWhen(false)] out string translatedName);

    bool TryTranslateTypeName(string obfuscatedName, [MaybeNullWhen(false)] out string translatedName);
}