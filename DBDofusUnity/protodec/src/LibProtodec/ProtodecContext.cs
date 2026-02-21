// Copyright © 2023-2026 Xpl0itR
// 
// This Source Code Form is subject to the terms of the Mozilla Public
// License, v. 2.0. If a copy of the MPL was not distributed with this
// file, You can obtain one at http://mozilla.org/MPL/2.0/.

using System;
using System.CodeDom.Compiler;
using System.Collections.Generic;
using System.Diagnostics;
using System.Diagnostics.CodeAnalysis;
using System.Linq;
using System.Runtime.CompilerServices;
using CommunityToolkit.Diagnostics;
using LibProtodec.Deobfuscation;
using LibProtodec.Models.Protobuf;
using LibProtodec.Models.Protobuf.Fields;
using LibProtodec.Models.Protobuf.TopLevels;
using LibProtodec.Models.Protobuf.Types;
using LibProtodec.Reflection;
using LibProtodec.Reflection.Il2Cpp;
using Microsoft.Extensions.Logging;
using SystemEx;
using ZLinq;

namespace LibProtodec;

// ReSharper disable ClassWithVirtualMembersNeverInherited.Global, MemberCanBePrivate.Global, MemberCanBeProtected.Global, PropertyCanBeMadeInitOnly.Global
public class ProtodecContext
{
    private readonly Dictionary<string, TopLevel> _parsed = [];

    public readonly List<Protobuf> Protobufs = [];

    public ILogger? Logger { get; set; }

    public INameTranslator? NameTranslator { get; set; }

    public void WriteAllTo(IndentedTextWriter writer)
    {
        writer.WriteLine("// Decompiled with protodec");
        writer.WriteLine();
        writer.WriteLine("""syntax = "proto3";""");
        writer.WriteLine();

        HashSet<string> wellKnownImports = Protobufs.SelectMany(static proto => proto.WellKnownImports).ToHashSet();
        if (wellKnownImports.Count > 0)
        {
            foreach (string import in wellKnownImports)
                Protobuf.WriteImportTo(writer, import);

            writer.WriteLine();
        }

        foreach (TopLevel topLevel in Protobufs.SelectMany(static proto => proto.TopLevels)
                                               .OrderBy(static topLevel => topLevel.Name))
        {
            topLevel.WriteTo(writer);
            writer.WriteLine();
            writer.WriteLine();
        }
    }

    public virtual Message ParseMessage(ICilType messageClass, CilParserOptions options = CilParserOptions.None)
    {
        Guard.IsTrue(messageClass is { IsClass: true, IsSealed: true });
        using IDisposable? _ = Logger?.BeginScopeParsingMessage(messageClass.FullName);

        if (_parsed.TryGetValue(messageClass.FullName, out TopLevel? parsedMessage))
        {
            Logger?.LogParsedMessage(parsedMessage.Name);
            return (Message)parsedMessage;
        }

        ICilTypeNameProvider messageTypeName = TranslateTypeName(messageClass);
        Message message = new()
        {
            Name       = messageTypeName.Name,
            IsObsolete = HasObsoleteAttribute(messageClass.CustomAttributes)
        };
        _parsed.Add(messageClass.FullName, message);

        Protobuf protobuf = GetProtobuf(messageClass, message, messageTypeName.Namespace, options);

        List<ICilField> idFields = messageClass.GetFields()
                                               .AsValueEnumerable()
                                               .Where(static field => field is { IsPublic: true, IsStatic: true, IsLiteral: true })
                                               .ToList();

        List<ICilProperty> properties = messageClass.GetProperties()
                                                    .AsValueEnumerable()
                                                    .Where(static property => property is { IsInherited: false, CanRead: true, Getter: { IsPublic: true, IsStatic: false, IsVirtual: false } })
                                                    .ToList();

        for (int pi = 0, fi = 0; pi < properties.Count; pi++)
        {
            ICilProperty property     = properties[pi];
            ICilType     propertyType = property.Type;

            using IDisposable? __ = Logger?.BeginScopeParsingProperty(property.Name, propertyType.FullName);

            if (IsEnabled(options, CilParserOptions.RequireGeneratedCodeAttributeForProperties) && !HasGeneratedCodeAttribute(property.CustomAttributes, "protoc"))
            {
                Logger?.LogSkippingPropertyWithoutGeneratedCodeAttribute();
                continue;
            }

            if (!IsEnabled(options, CilParserOptions.IncludePropertiesWithoutNonUserCodeAttribute) && !HasNonUserCodeAttribute(property.CustomAttributes))
            {
                Logger?.LogSkippingPropertyWithoutNonUserCodeAttribute();
                continue;
            }

            // only OneOf enums are defined nested directly in the message class
            if (propertyType.IsEnum && propertyType.DeclaringType?.Name == messageClass.Name)
            {
                string oneOfName = TranslateOneOfPropName(property.Name);
                Logger?.LogParsedOneOfField(oneOfName);

                List<int> oneOfProtoFieldIds = propertyType.GetFields()
                                                           .AsValueEnumerable()
                                                           .Where(static field => field.IsLiteral)
                                                           .Select(static field => (int)field.ConstantValue!)
                                                           .Where(static id => id > 0)
                                                           .ToList();

                message.OneOfs.Add(oneOfName, oneOfProtoFieldIds);
                continue;
            }

            bool msgFieldHasHasProp = false; // some field properties are immediately followed by an additional "Has" get-only boolean property
            if (properties.Count > pi + 1 && properties[pi + 1].Type.Name == nameof(Boolean) && !properties[pi + 1].CanWrite)
            {
                msgFieldHasHasProp = true;
                pi++;
            }

            MessageField field = new(message)
            {
                Type       = ParseFieldType(propertyType, options, protobuf),
                Name       = TranslateMessageFieldName(property.Name),
                IsObsolete = HasObsoleteAttribute(property.CustomAttributes),
                HasHasProp = msgFieldHasHasProp
            };

            if (idFields.Count <= fi)
            {
                Logger?.LogFailedToLocateIdField();
                message.UnkFields.Add(field);
            }
            else
            {
                field.Id = (int)idFields[fi].ConstantValue!;
                message.Fields.Add(field.Id.Value, field);
            }

            Logger?.LogParsedField(field.Name, field.Id, field.Type.Name);
            fi++;
        }

        Logger?.LogParsedMessage(message.Name);
        return message;
    }

    public virtual Enum ParseEnum(ICilType enumEnum, CilParserOptions options = CilParserOptions.None)
    {
        Guard.IsTrue(enumEnum.IsEnum);
        using IDisposable? _ = Logger?.BeginScopeParsingEnum(enumEnum.FullName);

        if (_parsed.TryGetValue(enumEnum.FullName, out TopLevel? parsedEnum))
        {
            Logger?.LogParsedEnum(parsedEnum.Name);
            return (Enum)parsedEnum;
        }

        ICilTypeNameProvider enumTypeName = TranslateTypeName(enumEnum);
        Enum @enum = new()
        {
            Name       = enumTypeName.Name,
            IsObsolete = HasObsoleteAttribute(enumEnum.CustomAttributes)
        };
        _parsed.Add(enumEnum.FullName, @enum);

        Protobuf protobuf = GetProtobuf(enumEnum, @enum, enumTypeName.Namespace, options);

        foreach (ICilField enumField in enumEnum.GetFields().AsValueEnumerable().Where(static field => field.IsLiteral))
        {
            using IDisposable? __ = Logger?.BeginScopeParsingField(enumField.Name);

            EnumField field = new()
            {
                Id         = (int)enumField.ConstantValue!,
                Name       = TranslateEnumFieldName(enumField.CustomAttributes, enumField.Name, @enum.Name),
                IsObsolete = HasObsoleteAttribute(enumField.CustomAttributes)
            };

            Logger?.LogParsedField(field.Name, field.Id);
            @enum.Fields.Add(field);
        }

        if (@enum.Fields.AsValueEnumerable().All(static field => field.Id != 0))
        {
            protobuf.Edition = "2023";
            @enum.IsClosed   = true;
        }

        Logger?.LogParsedEnum(@enum.Name);
        return @enum;
    }

    public virtual Service ParseService(ICilType serviceClass, CilParserOptions options = CilParserOptions.None)
    {
        Guard.IsTrue(serviceClass.IsClass);

        bool? isClientClass = null;
        if (serviceClass.IsAbstract)
        {
            if (serviceClass is { IsSealed: true, IsNested: false })
            {
                List<ICilType> nested = serviceClass.GetNestedTypes().ToList();
                serviceClass = nested.AsValueEnumerable().SingleOrDefault(static nested => nested is { IsAbstract: true, IsSealed  : false }) 
                            ?? nested.AsValueEnumerable().Single(static nested => nested is { IsClass            : true, IsAbstract: false });
            }
            
            if (serviceClass is { IsNested: true, IsAbstract: true, IsSealed: false })
            {
                isClientClass = false;
            }
        }

        if (serviceClass is { IsAbstract: false, IsNested: true, DeclaringType: not null })
        {
            isClientClass = true;
        }

        Guard.IsNotNull(isClientClass);
        using IDisposable? _ = Logger?.BeginScopeParsingService(serviceClass.DeclaringType!.FullName);

        if (_parsed.TryGetValue(serviceClass.DeclaringType!.FullName, out TopLevel? parsedService))
        {
            Logger?.LogParsedService(parsedService.Name);
            return (Service)parsedService;
        }

        ICilTypeNameProvider serviceTypeName = TranslateTypeName(serviceClass.DeclaringType);
        Service service = new()
        {
            Name       = serviceTypeName.Name,
            IsObsolete = HasObsoleteAttribute(serviceClass.CustomAttributes)
        };
        _parsed.Add(serviceClass.DeclaringType!.FullName, service);

        Protobuf protobuf = NewProtobuf(service, serviceClass.DeclaringAssemblyName, serviceTypeName.Namespace);

        foreach (ICilMethod cilMethod in serviceClass.GetMethods().AsValueEnumerable().Where(static method => method is { IsInherited: false, IsPublic: true, IsStatic: false, IsConstructor: false }))
        {
            using IDisposable? __ = Logger?.BeginScopeParsingMethod(cilMethod.Name);

            if (!IsEnabled(options, CilParserOptions.IncludeServiceMethodsWithoutGeneratedCodeAttribute)
             && !HasGeneratedCodeAttribute(cilMethod.CustomAttributes, "grpc_csharp_plugin"))
            {
                Logger?.LogSkippingMethodWithoutGeneratedCodeAttribute();
                continue;
            }

            ICilType requestType, responseType, returnType = cilMethod.ReturnType;
            bool streamReq, streamRes;

            if (isClientClass.Value)
            {
                ICilTypeNameProvider returnTypeName = TranslateTypeName(returnType);
                if (returnTypeName.Name == "AsyncUnaryCall`1")
                {
                    Logger?.LogSkippingDuplicateMethod();
                    continue;
                }

                List<ICilType> parameters = cilMethod.GetParameterTypes().ToList();
                if (parameters.Count > 2)
                {
                    Logger?.LogSkippingDuplicateMethod();
                    continue;
                }

                switch (returnType.GenericTypeArguments.Count)
                {
                    case 2:
                        requestType  = returnType.GenericTypeArguments[0];
                        responseType = returnType.GenericTypeArguments[1];
                        streamReq    = true;
                        streamRes    = returnTypeName.Name == "AsyncDuplexStreamingCall`2";
                        break;
                    case 1:
                        requestType  = parameters[0];
                        responseType = returnType.GenericTypeArguments[0];
                        streamReq    = false;
                        streamRes    = true;
                        break;
                    default:
                        requestType  = parameters[0];
                        responseType = returnType;
                        streamReq    = false;
                        streamRes    = false;
                        break;
                }
            }
            else
            {
                List<ICilType> parameters = cilMethod.GetParameterTypes().ToList();

                if (parameters[0].GenericTypeArguments.Count == 1)
                {
                    streamReq   = true;
                    requestType = parameters[0].GenericTypeArguments[0];
                }
                else
                {
                    streamReq   = false;
                    requestType = parameters[0];
                }

                if (returnType.GenericTypeArguments.Count == 1)
                {
                    streamRes    = false;
                    responseType = returnType.GenericTypeArguments[0];
                }
                else
                {
                    streamRes    = true;
                    responseType = parameters[1].GenericTypeArguments[0];
                }
            }

            ServiceMethod method = new(service)
            {
                Name               = TranslateMethodName(cilMethod.Name),
                IsObsolete         = HasObsoleteAttribute(cilMethod.CustomAttributes),
                RequestType        = ParseFieldType(requestType,  options, protobuf),
                ResponseType       = ParseFieldType(responseType, options, protobuf),
                IsRequestStreamed  = streamReq,
                IsResponseStreamed = streamRes
            };

            Logger?.LogParsedMethod(method.Name, method.RequestType.Name, method.ResponseType.Name);
            service.Methods.Add(method);
        }

        Logger?.LogParsedService(service.Name);
        return service;
    }

    protected IProtobufType ParseFieldType(ICilType type, CilParserOptions options, Protobuf referencingProtobuf)
    {
        switch (type.GenericTypeArguments.Count)
        {
            case 1:
                return new Repeated(
                    ParseFieldType(type.GenericTypeArguments[0], options, referencingProtobuf));
            case 2:
                return new Map(
                    ParseFieldType(type.GenericTypeArguments[0], options, referencingProtobuf),
                    ParseFieldType(type.GenericTypeArguments[1], options, referencingProtobuf));
        }

        if (!LookupType(type, out IProtobufType? fieldType))
        {
            if (type.IsEnum)
            {
                if (IsEnabled(options, CilParserOptions.SkipEnums))
                {
                    return Scalar.Int32;
                }

                fieldType = ParseEnum(type, options);
            }
            else
            {
                fieldType = ParseMessage(type, options);
            }
        }

        switch (fieldType)
        {
            case WellKnown wellKnown:
                referencingProtobuf.WellKnownImports.Add(
                    wellKnown.FileName);
                break;
            case INestableType nestableType:
                Protobuf protobuf = nestableType.Protobuf!;
                if (referencingProtobuf != protobuf)
                    referencingProtobuf.Imports.Add(
                        protobuf.FileName);
                break;
        }

        return fieldType;
    }

    protected virtual bool LookupType(ICilType cilType, [NotNullWhen(true)] out IProtobufType? protobufType)
    {
        switch (cilType.FullName)
        {
            case "System.String":
                protobufType = Scalar.String;
                break;
            case "System.Boolean":
                protobufType = Scalar.Bool;
                break;
            case "System.Double":
                protobufType = Scalar.Double;
                break;
            case "System.UInt32":
                protobufType = Scalar.UInt32;
                break;
            case "System.UInt64":
                protobufType = Scalar.UInt64;
                break;
            case "System.Int32":
                protobufType = Scalar.Int32;
                break;
            case "System.Int64":
                protobufType = Scalar.Int64;
                break;
            case "System.Single":
                protobufType = Scalar.Float;
                break;
            case "Google.Protobuf.ByteString":
                protobufType = Scalar.Bytes;
                break;

            case "Google.Protobuf.WellKnownTypes.Any":
                protobufType = WellKnown.Any;
                break;
            case "Google.Protobuf.WellKnownTypes.Api":
                protobufType = WellKnown.Api;
                break;
            case "Google.Protobuf.WellKnownTypes.BoolValue":
                protobufType = WellKnown.BoolValue;
                break;
            case "Google.Protobuf.WellKnownTypes.BytesValue":
                protobufType = WellKnown.BytesValue;
                break;
            case "Google.Protobuf.WellKnownTypes.DoubleValue":
                protobufType = WellKnown.DoubleValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Duration":
                protobufType = WellKnown.Duration;
                break;
            case "Google.Protobuf.WellKnownTypes.Empty":
                protobufType = WellKnown.Empty;
                break;
            case "Google.Protobuf.WellKnownTypes.Enum":
                protobufType = WellKnown.Enum;
                break;
            case "Google.Protobuf.WellKnownTypes.EnumValue":
                protobufType = WellKnown.EnumValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Field":
                protobufType = WellKnown.Field;
                break;
            case "Google.Protobuf.WellKnownTypes.FieldMask":
                protobufType = WellKnown.FieldMask;
                break;
            case "Google.Protobuf.WellKnownTypes.FloatValue":
                protobufType = WellKnown.FloatValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Int32Value":
                protobufType = WellKnown.Int32Value;
                break;
            case "Google.Protobuf.WellKnownTypes.Int64Value":
                protobufType = WellKnown.Int64Value;
                break;
            case "Google.Protobuf.WellKnownTypes.ListValue":
                protobufType = WellKnown.ListValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Method":
                protobufType = WellKnown.Method;
                break;
            case "Google.Protobuf.WellKnownTypes.Mixin":
                protobufType = WellKnown.Mixin;
                break;
            case "Google.Protobuf.WellKnownTypes.NullValue":
                protobufType = WellKnown.NullValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Option":
                protobufType = WellKnown.Option;
                break;
            case "Google.Protobuf.WellKnownTypes.SourceContext":
                protobufType = WellKnown.SourceContext;
                break;
            case "Google.Protobuf.WellKnownTypes.StringValue":
                protobufType = WellKnown.StringValue;
                break;
            case "Google.Protobuf.WellKnownTypes.Struct":
                protobufType = WellKnown.Struct;
                break;
            case "Google.Protobuf.WellKnownTypes.Syntax":
                protobufType = WellKnown.Syntax;
                break;
            case "Google.Protobuf.WellKnownTypes.Timestamp":
                protobufType = WellKnown.Timestamp;
                break;
            case "Google.Protobuf.WellKnownTypes.Type":
                protobufType = WellKnown.Type;
                break;
            case "Google.Protobuf.WellKnownTypes.UInt32Value":
                protobufType = WellKnown.UInt32Value;
                break;
            case "Google.Protobuf.WellKnownTypes.UInt64Value":
                protobufType = WellKnown.UInt64Value;
                break;
            case "Google.Protobuf.WellKnownTypes.Value":
                protobufType = WellKnown.Value;
                break;

            default:
                protobufType = null;
                return false;
        }

        return true;
    }

    protected Protobuf NewProtobuf(TopLevel topLevel, string declaringAssemblyName, string? @namespace)
    {
        Protobuf protobuf = new()
        {
            AssemblyName = declaringAssemblyName,
            Namespace    = @namespace
        };

        topLevel.Protobuf = protobuf;
        protobuf.TopLevels.Add(topLevel);
        Protobufs.Add(protobuf);

        return protobuf;
    }

    protected Protobuf GetProtobuf<T>(ICilType topLevelType, T topLevel, string? @namespace, CilParserOptions options)
        where T : TopLevel, INestableType
    {
        Protobuf protobuf;
        if (topLevelType.IsNested)
        {
            ICilType parent = topLevelType.DeclaringType!.DeclaringType!;
            if (!_parsed.TryGetValue(parent.FullName, out TopLevel? parentTopLevel))
            {
                parentTopLevel = ParseMessage(parent, options);
            }

            protobuf = parentTopLevel.Protobuf!;
            topLevel.Protobuf = protobuf;
            topLevel.Parent   = parentTopLevel;

            ((Message)parentTopLevel).Nested.Add(topLevelType.Name, topLevel);
        }
        else
        {
            protobuf = NewProtobuf(topLevel, topLevelType.DeclaringAssemblyName, @namespace);
        }

        return protobuf;
    }

    protected virtual bool TryReadFirstCtorArgAsString(ICilCustomAttribute attribute, [NotNullWhen(true)] out string? arg0)
    {
        arg0 = null;
        if (!attribute.HasConstructorArguments)
            return false;

        if (attribute is Il2CppGeneratorBackedAttribute)
            return false; //TODO: parse ctor arg generator

        object? arg = attribute.ConstructorArgumentValues[0];
        if (arg is not string str)
            return false;

        arg0 = str;
        return true;
    }

    protected ICilTypeNameProvider TranslateTypeName(ICilType type) =>
        NameTranslator?.TryTranslateTypeName(type.Name, out string? translatedName) == true
            ? new CilTypeName(translatedName)
            : type;

    protected string TranslateOneOfPropName(string oneOfPropName)
    {
        if (NameTranslator is not null)
        {
            if (NameTranslator.TryTranslateMemberName(oneOfPropName, out string? translatedName))
            {
                oneOfPropName = translatedName;
            }
            else if (NameTranslator.IsNameObfuscated(oneOfPropName))
            {
                return oneOfPropName;
            }
        }

        return StringExtensions.TrimEnd(oneOfPropName.AsSpan(), "Case").ToSnakeCaseLower();
    }

    protected string TranslateMessageFieldName(string fieldName)
    {
        if (NameTranslator is not null)
        {
            if (NameTranslator.TryTranslateMemberName(fieldName, out string? translatedName))
            {
                fieldName = translatedName;
            }
            else if (NameTranslator.IsNameObfuscated(fieldName))
            {
                return fieldName;
            }
        }

        return fieldName.ToSnakeCaseLower();
    }

    protected bool HasGeneratedCodeAttribute(IEnumerable<ICilCustomAttribute> attributes, string tool) =>
        attributes.AsValueEnumerable().Any(attr =>
            attr.Type.Name == nameof(GeneratedCodeAttribute)
         && (!TryReadFirstCtorArgAsString(attr, out string? arg0) || arg0 == tool /* If we can't read the first parameter, we assume it's fine™ */));

    protected static bool HasNonUserCodeAttribute(IEnumerable<ICilCustomAttribute> attributes) =>
        attributes.AsValueEnumerable().Any(static attr => attr.Type.Name == nameof(DebuggerNonUserCodeAttribute));

    protected static bool HasObsoleteAttribute(IEnumerable<ICilCustomAttribute> attributes) =>
        attributes.AsValueEnumerable().Any(static attr => attr.Type.Name == nameof(ObsoleteAttribute));

    [MethodImpl(MethodImplOptions.AggressiveInlining)]
    protected static bool IsEnabled(CilParserOptions options, CilParserOptions option) =>
        (options & option) == option;

    private string TranslateEnumFieldName(IEnumerable<ICilCustomAttribute> attributes, string fieldName, string enumName)
    {
        ICilCustomAttribute? nameAttr = attributes.AsValueEnumerable().SingleOrDefault(static attr => attr.Type.Name == "OriginalNameAttribute");
        if (nameAttr is not null && TryReadFirstCtorArgAsString(nameAttr, out string? originalName))
        {
            return originalName;
        }

        if (NameTranslator is not null)
        {
            if (NameTranslator.TryTranslateMemberName(fieldName, out string? translatedName))
            {
                fieldName = translatedName;
            }
            else if (!NameTranslator.IsNameObfuscated(fieldName))
            {
                fieldName = fieldName.ToSnakeCaseUpper();
            }

            if (!NameTranslator.IsNameObfuscated(enumName))
            {
                enumName = enumName.ToSnakeCaseUpper();
            }
        }

        return $"{enumName}_{fieldName}";
    }

    private string TranslateMethodName(string methodName) =>
        NameTranslator?.TryTranslateMemberName(methodName, out string? translatedName) == true
            ? translatedName
            : methodName;
}