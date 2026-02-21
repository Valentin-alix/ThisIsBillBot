// Copyright © 2024-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System.Collections.Generic;
using System.Text;
using CommunityToolkit.Diagnostics;
using LibCpp2IL.BinaryStructures;
using LibCpp2IL.Metadata;
using SystemEx.Memory;
using Il2CppTypeStruct = LibCpp2IL.BinaryStructures.Il2CppType;

namespace LibProtodec.Reflection.Il2Cpp;

public sealed class Il2CppCustomAttributeMetadata
{
    public readonly uint AttributeCount;

    private readonly Il2CppAssemblyLoader _loader;
    private readonly byte[]               _data;

    private uint[]?      _constructorIndices;
    private object?[][]? _constructorArgumentValues;

    public Il2CppCustomAttributeMetadata(Il2CppAssemblyLoader loader, int attrDataRngIdx)
    {
        Il2CppCustomAttributeDataRange attrDataRange   = loader.Metadata.AttributeDataRanges![attrDataRngIdx];
        Il2CppCustomAttributeDataRange attrDataRngNext = loader.Metadata.AttributeDataRanges[attrDataRngIdx + 1];

        long attrDataStart = loader.Metadata.metadataHeader.attributeData.Offset + attrDataRange.startOffset;
        long attrDataEnd   = loader.Metadata.metadataHeader.attributeData.Offset + attrDataRngNext.startOffset;

        AttributeCount = loader.Metadata.ReadUnityCompressedUIntAtRawAddr(attrDataStart, out int bytesRead);
        _data          = loader.Metadata.ReadByteArrayAtRawAddress(attrDataStart + bytesRead, checked((int)(attrDataEnd - attrDataStart - bytesRead)));
        _loader        = loader;
    }

    public IReadOnlyList<uint> ConstructorIndices
    {
        get
        {
            if (_constructorIndices is null)
            {
                MemoryReader reader = new(_data);

                _constructorIndices = new uint[AttributeCount];
                for (int i = 0; i < AttributeCount; i++)
                    _constructorIndices[i] = reader.ReadUInt32LittleEndian();
            }

            return _constructorIndices;
        }
    }

    public IReadOnlyList<IReadOnlyList<object?>> ConstructorArgumentValues
    {
        get
        {
            if (_constructorArgumentValues is null)
            {
                MemoryReader reader = new(_data) { Position = checked((int)AttributeCount) * sizeof(uint) };

                _constructorArgumentValues = new object[AttributeCount][];
                for (int i = 0; i < AttributeCount; i++)
                {
                    uint ctorArgCount = ReadUnityCompressedUInt32(ref reader);
                    uint fieldCount   = ReadUnityCompressedUInt32(ref reader);
                    uint propCount    = ReadUnityCompressedUInt32(ref reader);

                    _constructorArgumentValues[i] = ctorArgCount > 0
                        ? new object[ctorArgCount]
                        : [];

                    for (int j = 0; j < ctorArgCount; j++)
                        _constructorArgumentValues[i][j] = ReadValue(ref reader);

                    // read the rest just to exhaust the stream
                    for (uint j = 0; j < fieldCount; j++)
                    {
                        ReadValue(ref reader);
                        ResolveMember(ref reader);
                    }

                    for (uint j = 0; j < propCount; j++)
                    {
                        ReadValue(ref reader);
                        ResolveMember(ref reader);
                    }
                }
            }

            return _constructorArgumentValues;
        }
    }

    private static uint ReadUnityCompressedUInt32(ref MemoryReader reader)
    {
        byte @byte = reader.Read<byte>();

        switch (@byte)
        {
            case < 128:
                return @byte;
            case 240:
                return reader.ReadUInt32LittleEndian();
            case 254:
                return uint.MaxValue - 1;
            case byte.MaxValue:
                return uint.MaxValue;
        }

        if ((@byte & 192) == 192)
        {
            return (@byte & ~192U) << 24
                 | ((uint)reader.Read<byte>() << 16)
                 | ((uint)reader.Read<byte>() << 8)
                 | reader.Read<byte>();
        }

        if ((@byte & 128) == 128)
        {
            return (@byte & ~128U) << 8
                 | reader.Read<byte>();
        }

        return ThrowHelper.ThrowInvalidDataException<uint>();
    }

    private static int ReadUnityCompressedInt32(ref MemoryReader reader)
    {
        uint unsigned = ReadUnityCompressedUInt32(ref reader);
        if (unsigned == uint.MaxValue)
            return int.MinValue;

        bool isNegative = (unsigned & 1) == 1;
        unsigned >>= 1;

        return isNegative
            ? -(int)(unsigned + 1)
            : (int)unsigned;
    }

    private object? ReadValue(ref MemoryReader reader)
    {
        Il2CppTypeEnum type = (Il2CppTypeEnum)reader.Read<byte>();
        return ReadValue(ref reader, type);
    }

    private object? ReadValue(ref MemoryReader reader, Il2CppTypeEnum type)
    {
        switch (type)
        {
            case Il2CppTypeEnum.IL2CPP_TYPE_ENUM:
                Il2CppTypeEnum underlyingType = ReadEnumUnderlyingType(ref reader);
                return ReadValue(ref reader, underlyingType);
            case Il2CppTypeEnum.IL2CPP_TYPE_SZARRAY:
                return ReadSzArray(ref reader);
            case Il2CppTypeEnum.IL2CPP_TYPE_IL2CPP_TYPE_INDEX:
                return ReadIl2CppType(ref reader);
            case Il2CppTypeEnum.IL2CPP_TYPE_BOOLEAN:
                return reader.Read<bool>();
            case Il2CppTypeEnum.IL2CPP_TYPE_CHAR:
                return (char)reader.ReadInt16LittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_I1:
                return reader.Read<sbyte>();
            case Il2CppTypeEnum.IL2CPP_TYPE_U1:
                return reader.Read<byte>();
            case Il2CppTypeEnum.IL2CPP_TYPE_I2:
                return reader.ReadInt16LittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_U2:
                return reader.ReadUInt16LittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_I4:
                return ReadUnityCompressedInt32(ref reader);
            case Il2CppTypeEnum.IL2CPP_TYPE_U4:
                return ReadUnityCompressedUInt32(ref reader);
            case Il2CppTypeEnum.IL2CPP_TYPE_I8:
                return reader.ReadInt64LittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_U8:
                return reader.ReadUInt64LittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_R4:
                return reader.ReadSingleLittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_R8:
                return reader.ReadDoubleLittleEndian();
            case Il2CppTypeEnum.IL2CPP_TYPE_STRING:
                return ReadString(ref reader);
            default:
                return ThrowHelper.ThrowNotSupportedException<object>();
        }
    }

    private Il2CppTypeEnum ReadEnumUnderlyingType(ref MemoryReader reader)
    {
        int typeIdx = ReadUnityCompressedInt32(ref reader);
        var enumType = _loader.Binary.GetType(
            Il2CppVariableWidthIndex<Il2CppTypeStruct>.MakeTemporaryForFixedWidthUsage(typeIdx));

        return enumType.AsClass().EnumUnderlyingType.Type;
    }

    private object?[]? ReadSzArray(ref MemoryReader reader)
    {
        int arrayLength = ReadUnityCompressedInt32(ref reader);
        if (arrayLength == -1)
            return null;

        Il2CppTypeEnum arrayType = (Il2CppTypeEnum)reader.Read<byte>();
        if (arrayType == Il2CppTypeEnum.IL2CPP_TYPE_ENUM)
            arrayType = ReadEnumUnderlyingType(ref reader);

        bool typePrefixed = reader.Read<bool>();
        if (typePrefixed && arrayType != Il2CppTypeEnum.IL2CPP_TYPE_OBJECT)
            ThrowHelper.ThrowInvalidDataException("Array elements are type-prefixed, but the array type is not object");

        object?[] array = new object?[arrayLength];
        for (int i = 0; i < arrayLength; i++)
        {
            Il2CppTypeEnum elementType = typePrefixed
                ? (Il2CppTypeEnum)reader.Read<byte>()
                : arrayType;

            array[i] = ReadValue(ref reader, elementType);
        }

        return array;
    }

    private Il2CppTypeStruct? ReadIl2CppType(ref MemoryReader reader)
    {
        int typeIndex = ReadUnityCompressedInt32(ref reader);
        if (typeIndex == -1)
            return null;

        return _loader.Binary.GetType(
            Il2CppVariableWidthIndex<Il2CppTypeStruct>.MakeTemporaryForFixedWidthUsage(typeIndex));
    }

    private static string? ReadString(ref MemoryReader reader)
    {
        int length = ReadUnityCompressedInt32(ref reader);
        if (length == -1)
            return null;

        return Encoding.UTF8.GetString(
            reader.ReadSlice(length));
    }

    private static void ResolveMember(ref MemoryReader reader)
    {
        // We don't care about attribute properties or fields,
        // so we just read enough to exhaust the stream

        int memberIndex = ReadUnityCompressedInt32(ref reader);
        if (memberIndex < 0)
        {
            ReadUnityCompressedUInt32(ref reader);
        }
    }
}