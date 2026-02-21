// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using AssetRipper.Primitives;
using Microsoft.Extensions.Logging;

namespace LibProtodec.Reflection;

internal static partial class LoggerMessages
{
    [LoggerMessage(LogLevel.Error, "Failed to locate code registration struct.")]
    internal static partial void LogCodeRegNotFound(this ILogger logger);

    [LoggerMessage(LogLevel.Error, "Failed to locate metadata registration struct.")]
    internal static partial void LogMetaRegNotFound(this ILogger logger);

    [LoggerMessage(LogLevel.Warning, "Failed to load metadata, reattempting with Mfuscator demangler...")]
    internal static partial void LogMetadataAttemptingFallback(this ILogger logger);

    [LoggerMessage(LogLevel.Information, "Attempting to load metadata...")]
    internal static partial void LogLoadingMetadata(this ILogger logger);

    [LoggerMessage(LogLevel.Information, "Attempting to load binary...")]
    internal static partial void LogLoadingBinary(this ILogger logger);

    [LoggerMessage(LogLevel.Information, "Loaded {typeCount} types from {assemblyCount} assemblies for parsing.")]
    internal static partial void LogLoadedTypeAndAssemblyCount(this ILogger logger, int typeCount, int assemblyCount);

    [LoggerMessage(LogLevel.Information, "Parsed unity version as {unityVersion}")]
    internal static partial void LogParsedUnityVersion(this ILogger logger, UnityVersion unityVersion);

    [LoggerMessage(LogLevel.Debug, "Parsing unity version from {source}...")]
    internal static partial void LogParsingUnityVersion(this ILogger logger, string source);

    [LoggerMessage(LogLevel.Debug, "Mfuscator demangler returned failure:")]
    internal static partial void LogMfuscatorDemanglerFail(this ILogger logger, Exception ex);
}