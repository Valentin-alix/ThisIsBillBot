// Copyright © 2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using Microsoft.Extensions.Logging;
using Cpp2IlLogger = Cpp2IL.Core.Logging.Logger;

namespace LibProtodec.Reflection.Il2Cpp.Internal;

internal static class Cpp2IlLoggingAdapter
{
    internal static ILogger? Logger;

    static Cpp2IlLoggingAdapter()
    {
        Cpp2IlLogger.ErrorLog   += (message, source) => Logger?.Log(LogLevel.Error,       new EventId(0, source), message, null, MessageFormatter);
        Cpp2IlLogger.WarningLog += (message, source) => Logger?.Log(LogLevel.Warning,     new EventId(0, source), message, null, MessageFormatter);
        Cpp2IlLogger.InfoLog    += (message, source) => Logger?.Log(LogLevel.Information, new EventId(0, source), message, null, MessageFormatter);
        Cpp2IlLogger.VerboseLog += (message, source) => Logger?.Log(LogLevel.Debug,       new EventId(0, source), message, null, MessageFormatter);
    }

    private static readonly Func<string, Exception?, string> MessageFormatter = static (message, _) => message.Trim();
}