// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Runtime.ExceptionServices;
using AssetRipper.Primitives;
using CommunityToolkit.Diagnostics;
using Cpp2IL.Core.Api;
using LibCpp2IL;
using LibCpp2IL.BinaryStructures;
using LibCpp2IL.Logging;
using LibCpp2IL.Metadata;
using LibCpp2IL.Reflection;
using LibProtodec.Reflection.Il2Cpp.Internal;
using Microsoft.Extensions.Logging;
using Microsoft.Win32.SafeHandles;
using SystemEx.Memory;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppAssemblyLoader : ICilAssemblyLoader, IDisposable
{
    private readonly LibCpp2IlContext _libCpp2Il;

    private readonly Dictionary<string, Il2CppType> _typeCache = [];
    private readonly ILogger? _logger;

    public Il2CppAssemblyLoader(
        byte[]          assembly,
        byte[]          metadata,
        UnityVersion    unityVersion,
        ILoggerFactory? loggerFactory = null)
    {
        if (loggerFactory is not null)
        {
            _logger = loggerFactory.CreateLogger<Il2CppAssemblyLoader>();

            Cpp2IlLoggingAdapter.Logger ??=
                loggerFactory.CreateLogger<Cpp2IlPlugin>();

            if (LibLogger.Writer is not LibCpp2IlLoggingAdapter)
                LibLogger.Writer = new LibCpp2IlLoggingAdapter(
                    loggerFactory.CreateLogger(nameof(LibCpp2IL)));
        }

        Il2CppBinary.OnRegistrationStructLocationFailure += TryLocateRegistrationStructs;
        LibCpp2IlContextBuilder builder = new();

        _logger?.LogLoadingMetadata();
        try
        {
            builder.LoadMetadata(metadata, unityVersion);
        }
        catch (Exception ex)
        {
            var edi = ExceptionDispatchInfo.Capture(ex);

            _logger?.LogMetadataAttemptingFallback();
            try
            {
                metadata = MfuscatorDemangler.DemangleMetadata(metadata, unityVersion);
            }
            catch (Exception e)
            {
                _logger?.LogMfuscatorDemanglerFail(e);
                edi.Throw();
            }

            builder.LoadMetadata(metadata, unityVersion);
        }

        _logger?.LogLoadingBinary();
        builder.LoadBinary(assembly);

        _libCpp2Il = builder.Build();

        foreach (Il2CppTypeDefinition il2CppType in Metadata.typeDefs)
            _typeCache[il2CppType.FullName!] = new Il2CppType(this, il2CppType, []);

        _logger?.LogLoadedTypeAndAssemblyCount(_typeCache.Count, Metadata.imageDefinitions.Length);
    }

    public void Dispose()
    {
        Il2CppBinary.OnRegistrationStructLocationFailure -= TryLocateRegistrationStructs;
    }

    public Il2CppBinary Binary =>
        _libCpp2Il.Binary;

    public Il2CppMetadata Metadata =>
        _libCpp2Il.Metadata;

    public IReadOnlyList<ICilType> EnumerateTypes() =>
        _typeCache.Values.ToArray();

    public ICilType GetType(string typeFullName, string _) =>
        _typeCache[typeFullName]; // All typeDefs are cached by the end of the ctor

    internal ICilType GetType(Il2CppTypeDefinition il2CppType) =>
        _typeCache[il2CppType.FullName!]; // All typeDefs are cached by the end of the ctor

    internal ICilType GetType(Il2CppTypeReflectionData il2CppTypeData)
    {
        Guard.IsTrue(il2CppTypeData.isType);

        string key = il2CppTypeData.ToString();

        if (_typeCache.TryGetValue(key, out Il2CppType? cachedType))
            return cachedType;

        return _typeCache[key] = new Il2CppType(this, il2CppTypeData.baseType!, il2CppTypeData.genericParams);
    }

    private void TryLocateRegistrationStructs(
        Il2CppBinary                    binary,
        Il2CppMetadata                  metadata,
        ref Il2CppCodeRegistration?     codeReg,
        ref Il2CppMetadataRegistration? metaReg)
    {
        if (codeReg is null)
            StrippedCodeRegistrationLocator.TryLocate(binary, metadata, ref codeReg, ref metaReg);

        if (codeReg is null) _logger?.LogCodeRegNotFound();
        if (metaReg is null) _logger?.LogMetaRegNotFound();
    }

    public static Il2CppAssemblyLoader LoadFromFiles(
        string          assemblyPath,
        string          metadataPath,
        string          unityVersionParam,
        ILoggerFactory? loggerFactory = null)
    {
        ILogger? logger = loggerFactory?.CreateLogger<Il2CppAssemblyLoader>();

        UnityVersion unityVersion;
        if (unityVersionParam.EndsWith("data.unity3d", StringComparison.OrdinalIgnoreCase))
        {
            logger?.LogParsingUnityVersion("data.unity3d");

            unityVersion = ReadVersionFromDataUnity3D(unityVersionParam);
        }
        else if (unityVersionParam.EndsWith("globalgamemanagers", StringComparison.OrdinalIgnoreCase))
        {
            logger?.LogParsingUnityVersion("globalgamemanagers");

            unityVersion = ReadVersionFromGlobalGameManagers(unityVersionParam);
        }
        else
        {
            logger?.LogParsingUnityVersion("string");

            unityVersion = UnityVersion.Parse(unityVersionParam);
        }

        logger?.LogParsedUnityVersion(unityVersion);

        byte[] assembly = File.ReadAllBytes(assemblyPath),
               metadata = File.ReadAllBytes(metadataPath);

        return new Il2CppAssemblyLoader(
            assembly,
            metadata,
            unityVersion,
            loggerFactory);
    }

    private static UnityVersion ReadVersionFromDataUnity3D(string path)
    {
        using SafeFileHandle file = File.OpenHandle(path);
        
        Span<byte> buffer = stackalloc byte[0x10];
        RandomAccess.Read(file, buffer, 0x12);
        
        MemoryReader reader = new(buffer);
        string str = reader.ReadCString();

        return UnityVersion.Parse(str);
    }

    private static UnityVersion ReadVersionFromGlobalGameManagers(string path)
    {
        using SafeFileHandle file = File.OpenHandle(path);
        
        Span<byte> buffer = stackalloc byte[0x2C];
        RandomAccess.Read(file, buffer, 0x14);

        MemoryReader reader = new(buffer);

        if (reader.TryReadCString(out string? str) && UnityVersion.TryParse(str, out UnityVersion ver, out _))
            return ver;

        reader.Position = 0x1C;
        str = reader.ReadCString();

        return UnityVersion.Parse(str);
    }
}