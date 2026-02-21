// Copyright © 2024 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using LibCpp2IL.Logging;
using Microsoft.Extensions.Logging;

namespace LibProtodec.Reflection.Il2Cpp.Internal;

internal sealed class LibCpp2IlLoggingAdapter(ILogger logger) : LogWriter
{
    private static readonly Func<string, Exception?, string> MessageFormatter = static (message, _) => message.Trim();

    public override void Info(string message) =>
        logger.Log(LogLevel.Information, default(EventId), message, null, MessageFormatter);

    public override void Warn(string message) =>
        logger.Log(LogLevel.Warning, default(EventId), message, null, MessageFormatter);

    public override void Error(string message) =>
        logger.Log(LogLevel.Error, default(EventId), message, null, MessageFormatter);

    public override void Verbose(string message) =>
        logger.Log(LogLevel.Debug, default(EventId), message, null, MessageFormatter);
}