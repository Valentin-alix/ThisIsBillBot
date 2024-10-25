using System.Buffers;
using System.Reflection;
using System.Text;
using System.Text.Json;
using System.Text.RegularExpressions;
using IL2CppExtract.Assembly.IL2Cpp;
using IL2CppExtract.Assembly.Native;
using IL2CppExtract.Metadata;
using IL2CppExtract.Metadata.IL2Cpp;
using IL2CppExtract.Reader;

namespace IL2CppExtract.Assembly;

public partial class AssemblyFile
{
    public required PESection[] Sections { get; set; }
    public required uint PFuncTable { get; set; }
    public required ulong GlobalOffset { get; set; }
    public required PEOptionalHeader64 PE { get; set; }

    public ulong CodeRegistrationPointer { get; set; }
    public ulong MetadataRegistrationPointer { get; set; }

    public CodeRegistration CodeRegistration { get; set; }
    public MetadataRegistration MetadataRegistration { get; set; }
    public Dictionary<string, CodeGenModule> Modules { get; private set; } = new Dictionary<string, CodeGenModule>();
    public Dictionary<string, ulong> CodeGenModulePointers { get; } = new Dictionary<string, ulong>();
    public Dictionary<CodeGenModule, ulong[]> ModuleMethodPointers { get; set; } = new Dictionary<CodeGenModule, ulong[]>();
    // Only for >=v24.2. In earlier versions, invoker indices are stored in Il2CppMethodDefinition in the metadata file
    public Dictionary<CodeGenModule, int[]> MethodInvokerIndices { get; set; } = new Dictionary<CodeGenModule, int[]>();
    public long[] FieldOffsetPointers { get; private set; } = [];
    // Every type reference index sorted by virtual address
    public Dictionary<ulong, int> TypeReferenceIndicesByAddress { get; private set; } = new Dictionary<ulong, int>();
    // Every type reference (TypeRef) sorted by index
    public CppType[] TypeReferences { get; private set; } = [];
    public ulong[] MethodInvokePointers { get; set; } = [];
    public ulong[] FunctionAddresses { get; set; } = [];
    public CppGenericInst[] GenericInstances { get; private set; } = [];
    public CppTypeDefinitionSizes[] TypeDefinitionSizes { get; private set; } = [];
    public Dictionary<string, ulong> Methods = new Dictionary<string, ulong>();
    public Dictionary<string, ulong> Types = new Dictionary<string, ulong>();

    public required MetadataFile Metadata { get; init; }
    public required BinaryReader Reader { get; init; }

    public static AssemblyFile Read(FileStream stream, MetadataFile metadataFile)
    {
        var reader = new BinaryReader(stream);

        var file = AssemblyFile.ReadHeader(reader, metadataFile);

        var (codeRegistration, metadataRegistration) = file.ScanImage(reader, metadataFile);

        if (codeRegistration == 0 || metadataRegistration == 0)
        {
            throw new Exception("Can't find codeRegistration and metadataRegistration");
        }
        
        file.CodeRegistrationPointer = codeRegistration;
        file.MetadataRegistrationPointer = metadataRegistration;

        file.CodeRegistration = file.ReadCodeRegistration(reader, metadataFile.Version);
        file.MetadataRegistration = file.ReadMetadataRegistration(reader, metadataFile.Version);

        if (metadataFile.Header.Version == 29 && file.CodeRegistration.GenericMethodPointersCount > 0x50000)
        {
            metadataFile.Version = 29.1;
            file.CodeRegistrationPointer -= 2 * 8;
            file.CodeRegistration = file.ReadCodeRegistration(reader, metadataFile.Version);
        }

        // Do basic validatation that MetadataRegistration and CodeRegistration are sane
        if (metadataFile.Types.Length != file.MetadataRegistration.TypeDefinitionsSizesCount)
        {
            throw new Exception("Invalid MetadataRegistration, file is corrupted ! (or reader not up to date)");
        }

        if (file.CodeRegistration.ReversePInvokeWrappersCount > 0x10000 ||
            file.CodeRegistration.UnresolvedVirtualCallCount > 0x4000 ||
            file.CodeRegistration.InteropDataCount > 0x1000)
        {
            throw new Exception("Invalid CodeRegistration, file is corrupted ! (or reader not up to date)");
        }

        var codeGenModulePointers = file.ReadULongArray(reader, file.CodeRegistration.CodeGenModules, (int)file.CodeRegistration.CodeGenModulesCount);
        var modules = file.ReadCodeGenArray(reader,
            file.CodeRegistration.CodeGenModules,
            (int)file.CodeRegistration.CodeGenModulesCount,
            metadataFile.Version);

        foreach (var mp in modules.Zip(codeGenModulePointers, (m, p) => new
                 {
                     Module = m,
                     Pointer = p
                 }))
        {
            var module = mp.Module;

            var name = file.ReadMappedNullTerminatedString(reader, module.ModuleName);

            file.Modules.Add(name, module);
            file.CodeGenModulePointers.Add(name, mp.Pointer);

            // Read method pointers
            // If a module contains only interfaces, abstract methods and/or non-concrete generic methods,
            // the entire method pointer array will be NULL values, causing the methodPointer to be mapped to .bss
            // and therefore out of scope of the binary image
            try
            {
                file.ModuleMethodPointers.Add(module, file.ReadULongArray(reader, module.MethodPointers, (int)module.MethodPointerCount));
            }
            catch (InvalidOperationException)
            {
                file.ModuleMethodPointers.Add(module, new ulong[module.MethodPointerCount]);
            }

            // Read method invoker pointer indices - one per method
            file.MethodInvokerIndices.Add(module, file.ReadIntArray(reader, module.InvokerIndices, (int)module.MethodPointerCount));
        }

        // Field offset data. Metadata <=21.x uses a value-type array; >=21.x uses a pointer array
        // Versions from 22 onwards use an array of pointers in Binary.FieldOffsetData
        var fieldOffsetsArePointers = (metadataFile.Version >= 22);

        if (!fieldOffsetsArePointers)
        {
            throw new Exception($"Unsupported version {metadataFile.Version}");
        }

        file.FieldOffsetPointers = file.ReadMappedWordArray(reader,
            file.MetadataRegistration.FieldOffsets,
            (int)file.MetadataRegistration.FieldOffsetsCount);

        // Type references (pointer array)
        var typeRefPointers = file.ReadULongArray(reader,
            file.MetadataRegistration.Types,
            (int)file.MetadataRegistration.TypesCount);

        file.TypeReferenceIndicesByAddress = typeRefPointers.Zip(Enumerable.Range(0, typeRefPointers.Length), (a, i) => new
            {
                a,
                i
            })
            .ToDictionary(x => x.a, x => x.i);

        file.TypeReferences = file.ReadCppTypeArray(reader,
            file.MetadataRegistration.Types,
            (int)file.MetadataRegistration.TypesCount);

        // Method.Invoke function pointers
        file.MethodInvokePointers = file.ReadULongArray(reader, file.CodeRegistration.InvokerPointers, (int)file.CodeRegistration.InvokerPointersCount);
        file.FunctionAddresses = file.MethodInvokePointers.OrderBy(x => x).ToArray();
        // TODO: Function pointers as shown below
        // reversePInvokeWrappers
        // <=22: delegateWrappersFromManagedToNative, marshalingFunctions
        // >=21 <=22: ccwMarshalingFunctions
        // >=22: unresolvedVirtualCallPointers
        // >=23: interopData

        // Generic type and method specs (open and closed constructed types)
        file.GenericInstances = file.ReadCppGenericInst(reader, file.MetadataRegistration.GenericInsts, (int)file.MetadataRegistration.GenericInstsCount);
        file.TypeDefinitionSizes = file.ReadCppTypeDefinitionSizes(reader, file.MetadataRegistration.TypeDefinitionsSizes, (int)file.MetadataRegistration.TypeDefinitionsSizesCount);

        TypeContainer.TypesByDefinitionIndex = new AssemblyCppType[file.Metadata.Types.Length];
        TypeContainer.TypesByReferenceIndex = new AssemblyCppType[file.TypeReferences.Length];

        file.Metadata.GenerateFieldDefaultDictionary(file);
        
        var assemblies = new AssemblyCpp[file.Metadata.Images.Length];

        for (var index = 0; index < file.Metadata.Images.Length; index++)
        {
            assemblies[index] = new AssemblyCpp(file, index);
        }
        
        // Create and reference types from TypeRefs
        // Note that you can't resolve any TypeRefs until all the TypeDefs have been processed
        for (var typeRefIndex = 0; typeRefIndex < file.TypeReferences.Length; typeRefIndex++)
        {
            var typeRef = file.TypeReferences[typeRefIndex];
            
            var referencedType = file.ResolveTypeReference(typeRef);

            if (referencedType != null)
            {
                TypeContainer.TypesByReferenceIndex[typeRefIndex] = referencedType;
            }
        }

        return file;
    }
    public ulong? GetMethodPointer(CodeGenModule module, MethodDefinition methodDef)
    {
        // Find method pointer
        if (methodDef.MethodIndex < 0)
            return null;

        // Global method pointer array
        if (Metadata.Version <= 29)
        {
            throw new Exception("Unsupported version");
        }
        
        ulong start = 0;
        
        // Per-module method pointer array uses the bottom 24 bits of the method's metadata token
        // Derived from il2cpp::vm::MetadataCache::GetMethodPointer
        if (Metadata.Version >= 24.2)
        {
            var method = (methodDef.Token & 0xffffff);
            if (method == 0)
                return null;

            // In the event of an exception, the method pointer is not set in the file
            // This probably means it has been optimized away by the compiler, or is an unused generic method
            try 
            {
                // Remove ARM Thumb marker LSB if necessary
                start = ModuleMethodPointers[module][method - 1];
            }
            catch (IndexOutOfRangeException)
            {
                return null;
            }
        }
        
        if (start == 0)
            return null;
        
        return start;
    }
    public void ExportStaticStrings()
    {
        const string outputDir = "Output";
        
        Directory.CreateDirectory(outputDir);
        
        File.WriteAllText(Path.Combine(outputDir, "Methods.json"), JsonSerializer.Serialize(Methods, new JsonSerializerOptions()
        {
            WriteIndented = true
        }));

        var reflectorClasses = new Dictionary<string, List<string>>();


        var xored = false;
        
        foreach (var type in TypeContainer.TypesByDefinitionIndex)
        {
            if (!type.Assembly.Name.Contains("Protocol"))
            {
                continue;
            }
            
            var dir = Path.Combine(outputDir, type.Assembly.Name);
            
            if (!reflectorClasses.TryGetValue(dir, out var classes))
            {
                classes = new List<string>();
                reflectorClasses[dir] = classes;
            }

            if (type.FullName == null || type.FullName.Contains("<>c") || type.FullName.Contains("MonoScriptData"))
            {
                continue;
            }

            if (type.FullName.Length <= 2)
            {
                continue;
            }

            if (type.FullName == "Error")
            {
                continue;
            }
            
            if(type.FullName.Contains("<Module>"))
            {
                continue;
            }
            
            if(type.FullName.Contains("PrivateImplementationDetails"))
            {
                continue;
            }

            if (type.IsEnum)
            {
                continue;
            }

            if (type.Fields.Length == 0)
            {
                continue;
            }

            if (type.MemberType.HasFlag(MemberTypes.NestedType))
            {
                continue;
            }

            classes.Add(type.FullName);
        }

        foreach (var dir in reflectorClasses)
        {
            Directory.CreateDirectory(dir.Key);
            
            File.WriteAllText(Path.Combine(dir.Key, "Classes.json"), JsonSerializer.Serialize(dir.Value, new JsonSerializerOptions()
            {
                WriteIndented = true
            }));
        }
       
        var counter = new Dictionary<string, int>();
        
        foreach (var rva in TypeContainer.RVAFields)
        {
            // Ici on kiff et on export tout
            //if (!rva.FieldType.Type.Assembly.Name.Contains("Protocol"))
            //{
            //    continue;
            //}

            var dir = Path.Combine(outputDir, rva.FieldType.Type.Assembly.Name);

            var buffer = rva.GetFieldRVABuffer(this);

            // detect xor ?
            // certain string sont xor mais on n'a pas vraiment de quoi détecter lesquel le son ou non vu que les static field c'est un peu tout est n'importe quoi
            // donc on va dire qu'on laisse ça là si jamais on veut recup le reste on a juste a inversé ce bool
            if (xored)
            {
                var decryptedBuffer = new byte[buffer.Length];
                for (var i = 0; i < buffer.Length; i++)
                {
                    var b = buffer[i];
                    var key = (i ^ 0xAA) & 0xFF;
                    var decryptedByte = b ^ key;
                    decryptedBuffer[i] = (byte)decryptedByte;
                }
                
                buffer = decryptedBuffer;
            }

            // Utile quand c'est pas un protocol
            //if (rva.Name != "a_")
            //   continue;
            
            if(counter.TryGetValue(rva.Name, out var count))
            {
                counter[rva.Name] = count + 1;
            }
            else
            {
                counter[rva.Name] = 1;
            }
            
            Directory.CreateDirectory(dir);

            // Oui bon connard
            var str = Encoding.UTF8.GetString(buffer);
            if (str.Contains("Com.Ankama.Dofus.Server.Game.Protocol") || str.Contains("Com.Ankama.Dofus.Server.Connection.Protocol"))
            {        
                File.WriteAllBytes(Path.Combine(dir, "Types.bin"), buffer);
                continue;
            }
            
            File.WriteAllBytes(Path.Combine(dir, rva.Name + ".bin"), buffer);
        }
    }

    // Initialize type from type reference (TypeRef)
    // Much of the following is adapted from il2cpp::vm::Class::FromIl2CppType
    private AssemblyCppType? ResolveTypeReference(CppType typeRef)
    {
        AssemblyCppType? underlyingType = null;
        AssemblyCppType? elementType = null;
        
        switch (typeRef.Type)
        {
            // Classes defined in the metadata (reference to a TypeDef)
            case CppTypeEnum.Il2CppTypeClass:
            case CppTypeEnum.Il2CppTypeValuetype:
                underlyingType = TypeContainer.TypesByDefinitionIndex[typeRef.DataPoint]; // klassIndex
                break;

            case CppTypeEnum.Il2CppTypeArray:
                Reader.BaseStream.Seek(MapVATR(typeRef.DataPoint), SeekOrigin.Begin);
                var cppArrayType = CppArrayType.Read(Reader);
                elementType = GetTypeFromVirtualAddress(cppArrayType.EType);
                underlyingType = elementType?.MakeArrayType(cppArrayType.Rank);
                break;
            case CppTypeEnum.Il2CppTypeSzarray:
                elementType = GetTypeFromVirtualAddress(typeRef.DataPoint);
                underlyingType = elementType?.MakeArrayType(1);
                break;
            case CppTypeEnum.Il2CppTypePtr:
                break;
            // Generic type and generic method parameters
            case CppTypeEnum.Il2CppTypeVar:
            case CppTypeEnum.Il2CppTypeMvar:
                break;
            default:
                underlyingType = GetTypeDefinitionFromTypeEnum(typeRef.Type);
                break;

        }

        return underlyingType;
    }
    
    // Basic primitive types are specified via a flag value
    public AssemblyCppType? GetTypeDefinitionFromTypeEnum(CppTypeEnum t)
    {
        // IL2CPP_TYPE_IL2CPP_TYPE_INDEX is handled seperately because it has enum value 0xff
        var fqn = t switch
        {
            CppTypeEnum.Il2CppTypeIl2CppTypeIndex => "System.Type",
            CppTypeEnum.Il2CppTypeSzarray => "System.Array",
            _ => (int) t >= Constants.FullNameTypeString.Count
                ? null
                : Constants.FullNameTypeString[(int) t]
        };

        return fqn == null
            ? null
            : TypeContainer.TypesByFullName.GetValueOrDefault(fqn);
    }
    
    // Get a TypeRef by its virtual address
    // These are always nested types from references within another TypeRef
    private AssemblyCppType? GetTypeFromVirtualAddress(ulong ptr)
    {
        var typeRefIndex = TypeReferenceIndicesByAddress[ptr];

        if (TypeContainer.TypesByReferenceIndex[typeRefIndex] != null)
            return TypeContainer.TypesByReferenceIndex[typeRefIndex];

        var type = TypeReferences[typeRefIndex];
        var referencedType = ResolveTypeReference(type);
        
        TypeContainer.TypesByReferenceIndex[typeRefIndex] = referencedType;
        return referencedType;
    }


    private CodeRegistration ReadCodeRegistration(BinaryReader reader, double version)
    {
        reader.BaseStream.Seek(MapVATR(CodeRegistrationPointer), SeekOrigin.Begin);
        return CodeRegistration.Read(reader, version);
    }
    
    private MetadataRegistration ReadMetadataRegistration(BinaryReader reader, double version)
    {
        reader.BaseStream.Seek(MapVATR(MetadataRegistrationPointer), SeekOrigin.Begin);
        return MetadataRegistration.Read(reader, version);
    }

    private static AssemblyFile ReadHeader(BinaryReader reader, MetadataFile metadataFile)
    {
        // Check for MZ signature "MZ"
        var header = reader.ReadUInt16();
        
        if (header != 0x5A4D)
        {
            throw new Exception($"Invalid header: {header}");
        }

        reader.BaseStream.Seek(0x3C, SeekOrigin.Begin);
        var position = reader.ReadUInt32();
        reader.BaseStream.Seek(position, SeekOrigin.Begin);

        // Check PE signature "PE\0\0"
        if (reader.ReadUInt32() != 0x00004550)
        {
            throw new Exception("Invalid PE signature");
        }

        var coffHeader = CoffHeader.Read(reader);

        var size = coffHeader.SizeOfOptionalHeader switch
        {
            0xE0 => 32,
            0xF0 => 64,
            _ => throw new Exception($"Unknown header {coffHeader.SizeOfOptionalHeader}")
        };
        
        // Read PE optional header
        if (size == 32)
        {
            throw new Exception($"Unsupported PE Optional header of 32 bits");
        }

        var pe = PEOptionalHeader64.Read(reader);
        
        // Get IAT
        var iatStart = pe.DataDirectory[12].VirtualAddress;
        var iatSize = pe.DataDirectory[12].Size;

        var sections = new PESection[coffHeader.NumberOfSections];
        for (var i = 0; i < coffHeader.NumberOfSections; i++)
        {
            sections[i] = PESection.Read(reader);
        }

        var globalOffset = pe.ImageBase + pe.BaseOfCode - sections.First(x => x.Name == ".text").PointerToRawData;
        
        // Confirm that .rdata section begins at same place as IAT
        var rData = sections.First(x => x.Name == ".rdata");

        if (rData.VirtualAddress != iatStart)
        {
            throw new Exception("Error: the file could be packed or obfuscated");
        }
        
        // Calculate start of function pointer table
        var pFuncTable = rData.PointerToRawData + iatSize;
        
        // Skip over __guard_check_icall_fptr and __guard_dispatch_icall_fptr if present, then the following zero offset
        reader.BaseStream.Seek(pFuncTable, SeekOrigin.Begin);

        // 64 Bits only
        {
            while (reader.ReadUInt64() != 0)
            {
                pFuncTable += 8;
            }

            pFuncTable += 8;
        }
        
        return new AssemblyFile
        {
            Sections = sections,
            PFuncTable = pFuncTable,
            GlobalOffset = globalOffset,
            PE = pe,
            Reader = reader,
            Metadata = metadataFile
        };
    }


    private ulong MapFileOffsetToVA(uint offset)
    {
        var section = Sections.FirstOrDefault(x => offset >= x.PointerToRawData && offset < x.PointerToRawData + x.SizeOfRawData);

        if (section == null)
            return ulong.MaxValue;
        
        return PE.ImageBase + section.VirtualAddress + offset - section.PointerToRawData;
    }
    
    // Try to map an offset into the file image to an RVA
    public bool TryMapFileOffsetToVA(uint offset, out ulong va)
    {
        va = MapFileOffsetToVA(offset);

        if (va != ulong.MaxValue)
            return true;
        
        va = 0;
        return false;

    }

    private (ulong CodeRegistration, ulong MetadataRegistration) ScanImage(BinaryReader reader, MetadataFile metadata)
    {
        reader.BaseStream.Seek(0, SeekOrigin.Begin);
        // we read all bytes in memory...
        var bytes = reader.ReadBytes((int)reader.BaseStream.Length);
        // 64 bits
        const int ptrSize = 64 / 8;
        var imagesCount = metadata.Images.Length;

        if (metadata.Version < 27)
        {
            throw new Exception($"Unsupported version {metadata.Version}");
        }

        // Find CodeRegistration
        // >= 24.2
        // < 27: mscorlib.dll is always the first CodeGenModule
        // >= 27: mscorlib.dll is always the last CodeGenModule (Assembly-CSharp.dll is always the first but non-Unity builds don't have this DLL)
        //        NOTE: winrt.dll + other DLLs can come after mscorlib.dll so we can't use its location to get an accurate module count

        ulong codeRegVa = 0L;

        foreach (var offset in FindAllStrings(bytes, "mscorlib.dll\0"))
        {
            if (!TryMapFileOffsetToVA(offset, out var va))
            {
                continue;
            }

            foreach (var potentialCodeGenModules in FindAllPointerChains(bytes, va, 2))
            {
                if (codeRegVa != 0)
                    break;

                for (var i = imagesCount - 1; i >= 0; i--)
                {
                    if (codeRegVa != 0)
                        break;

                    foreach (var potentialCodeRegistrationPtr in FindAllPointerChains(bytes,
                                 potentialCodeGenModules - (ulong)i * ptrSize, 1))
                    {
                        var expectedImageCountPtr = potentialCodeRegistrationPtr - ptrSize;
                        var expectedImageCount = ReadMappedInt64(reader, expectedImageCountPtr);
                        if (expectedImageCount == imagesCount)
                        {
                            codeRegVa = potentialCodeRegistrationPtr;
                            break;
                        }
                    }
                }
            }
        }

        if (codeRegVa == 0)
            return (0, 0);
        
        // pCodeGenModules is the last field in CodeRegistration so we subtract the size of one pointer from the struct size
        var codeRegistration = codeRegVa - (CodeRegistration.GetSize(metadata.Version) - ptrSize);
        // reader.BaseStream.Seek(MapVATR(codeRegistration), SeekOrigin.Begin);
        // var cr = CodeRegistration.Read(reader, metadata.Version);
        
        // Lets find MetadataRegistraiton
        var metadataRegistration = 0UL;

        var size = (ulong)MetadataRegistration.GetSize(metadata.Version);
        var typesLength = (ulong)metadata.Types.Length;
        
        var vas = FindAllMappedWords(bytes, typesLength).Select(a => a - size + ptrSize * 4);
        var mrFieldCount = size / 8;
        foreach (var va in vas)
        {
            var mrWords = ReadMappedWordArray(reader, va, (int)mrFieldCount);
            
            // Even field indices are counts, odd field indices are pointers
            var ok = true;

            if (!mrWords.All(x => x >= 0))
                continue;
            
            for (var i = 0; i < mrWords.Length && ok; i++)
            {
                ok = i % 2 == 0 || TryMapVATR((ulong)mrWords[i], out _);
            }

            if (ok)
                metadataRegistration = va;
        }

        if (metadataRegistration == 0)
            return (0, 0);
        
        return (codeRegistration, metadataRegistration);
    }


    private IEnumerable<uint> FindAllStrings(byte[] blob, string str) =>
        FindAllBytes(blob, Encoding.ASCII.GetBytes(str), 1);
    
    // Boyer-Moore-Horspool
    public IEnumerable<uint> FindAllBytes(byte[] blob, byte[] signature, uint requiredAlignment = 1)
    { 
        var badBytes = ArrayPool<uint>.Shared.Rent(256);
        var signatureLength = (uint) signature.Length;

        for (uint i = 0; i < 256; i++)
        {
            badBytes[(int)i] = signatureLength;
        }

        var lastSignatureIndex = signatureLength - 1;

        for (uint i = 0; i < lastSignatureIndex; i++)
        {
            badBytes[signature[(int)i]] = lastSignatureIndex - i;
        }

        var blobLength = blob.Length;
        var currentIndex = 0u;

        while (currentIndex <= blobLength - signatureLength)
        {
            for (var i = lastSignatureIndex; blob[currentIndex + i] == signature[(int)i]; i--)
            {
                if (i != 0)
                    continue;
                
                yield return currentIndex;
                break;
            }

            currentIndex += badBytes[blob[currentIndex + lastSignatureIndex]];

            var alignment = currentIndex % requiredAlignment;
            if (alignment != 0)
                currentIndex += requiredAlignment - alignment;
        }

        ArrayPool<uint>.Shared.Return(badBytes);
    }
    
    private IEnumerable<ulong> FindAllPointerChains(byte[] blob, ulong va, int indirections) 
    {
        foreach (var vas in FindAllMappedWords(blob, va))
        {
            if (indirections == 1)
            {
                yield return vas;
            }
            else
            {
                foreach (var foundPointer in FindAllPointerChains(blob, vas, indirections - 1))
                {
                    yield return foundPointer;
                }
            }
        }

        //IEnumerable<ulong> vas = va;
        //for (int i = 0; i < indirections; i++)
        //    vas = FindAllMappedWords(blob, vas);
        //return vas;
    }
    
    // Find all valid virtual address pointers to a virtual address
    private IEnumerable<ulong> FindAllMappedWords(byte[] blob, ulong va)
    {
        var fileOffsets = FindAllWords(blob, va);
        foreach (var offset in fileOffsets)
            if (TryMapFileOffsetToVA(offset, out va))
                yield return va;
    }
    
    // Find 64-bit words
    private IEnumerable<uint> FindAllQWords(byte[] blob, ulong word) => FindAllBytes(blob, BitConverter.GetBytes(word), 8);

    private IEnumerable<uint> FindAllWords(byte[] blob, ulong word)
        => FindAllQWords(blob, word);

    private long ReadMappedInt64(BinaryReader reader, ulong uiAddr)
    {
        var position = MapVATR(uiAddr);
        reader.BaseStream.Seek(position, SeekOrigin.Begin);

        return reader.ReadInt64();
    }

    private long[] ReadMappedWordArray(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);

        var result = new long[count];
        for (var i = 0; i < count; i++)
        {
            result[i] = reader.ReadInt64();
        }

        return result;
    }
    
    private int[] ReadIntArray(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);

        var result = new int[count];
        for (var i = 0; i < count; i++)
        {
            result[i] = reader.ReadInt32();
        }

        return result;
    }
    
    private ulong[] ReadULongArray(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);

        var result = new ulong[count];
        for (var i = 0; i < count; i++)
        {
            result[i] = reader.ReadUInt64();
        }

        return result;
    }

    private CppType[] ReadCppTypeArray(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);
        var pointers = ReadULongArray(reader, uiAddr, count);
        
        var result = new CppType[count];
        for (var i = 0; i < count; i++)
        {     
            reader.BaseStream.Seek(MapVATR(pointers[i]), SeekOrigin.Begin);
            result[i] = CppType.Read(reader);
        }

        return result;
    }
    
    private CppGenericInst[] ReadCppGenericInst(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);
        var pointers = ReadULongArray(reader, uiAddr, count);
        
        var result = new CppGenericInst[count];
        for (var i = 0; i < count; i++)
        {     
            reader.BaseStream.Seek(MapVATR(pointers[i]), SeekOrigin.Begin);
            result[i] = CppGenericInst.Read(reader);
        }

        return result;
    }

    private CppTypeDefinitionSizes[] ReadCppTypeDefinitionSizes(BinaryReader reader, ulong uiAddr, int count)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);
        var pointers = ReadULongArray(reader, uiAddr, count);
        
        var result = new CppTypeDefinitionSizes[count];
        for (var i = 0; i < count; i++)
        {     
            reader.BaseStream.Seek(MapVATR(pointers[i]), SeekOrigin.Begin);
            result[i] = CppTypeDefinitionSizes.Read(reader);
        }

        return result;
    }
    
    private CodeGenModule[] ReadCodeGenArray(BinaryReader reader, ulong uiAddr, int count, double version)
    {
        if (count == 0)
            return [];

        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);
        var pointers = ReadULongArray(reader, uiAddr, count);
        
        var result = new CodeGenModule[count];
        for (var i = 0; i < count; i++)
        {     
            reader.BaseStream.Seek(MapVATR(pointers[i]), SeekOrigin.Begin);
            result[i] = CodeGenModule.Read(reader, version);
        }

        return result;
    }

    private string ReadMappedNullTerminatedString(BinaryReader reader, ulong uiAddr)
    {
        reader.BaseStream.Seek(MapVATR(uiAddr), SeekOrigin.Begin);

        return ReaderUtils.ReadNullTerminatedString(reader);
    }
    private bool TryMapVATR(ulong uiAddr, out uint result)
    {
        try 
        {
            result = MapVATR(uiAddr);
            return true;
        } 
        catch (InvalidOperationException) {
            result = 0;
            return false;
        }
    }
    
    private uint MapVATR(ulong uiAddr)
    {
        if (uiAddr == 0)
            return 0;

        var section = Sections.First(x => uiAddr - PE.ImageBase >= x.VirtualAddress &&
                                          uiAddr - PE.ImageBase < x.VirtualAddress + x.SizeOfRawData);
        return (uint) (uiAddr - section.VirtualAddress - PE.ImageBase + section.PointerToRawData);
    }

}