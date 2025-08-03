using AssetsTools.NET;
using AssetsTools.NET.Extra;
using Avalonia.Controls.Documents;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;
using SixLabors.ImageSharp;
using SixLabors.ImageSharp.PixelFormats;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Threading.Tasks;

namespace UABEAvalonia
{
    public class CommandLineHandler
    {
        public static void PrintHelp()
        {
            Console.WriteLine("UABE AVALONIA");
            Console.WriteLine("WARNING: Command line support VERY EARLY");
            Console.WriteLine("There is a high chance of stuff breaking");
            Console.WriteLine("Use at your own risk");
            Console.WriteLine("  UABEAvalonia batchexportbundle <directory>");
            Console.WriteLine("  UABEAvalonia batchimportbundle <directory>");
            Console.WriteLine("  UABEAvalonia applyemip <emip file> <directory>");
            Console.WriteLine("Bundle import/export arguments:");
            Console.WriteLine("  -keepnames writes out to the exact file name in the bundle.");
            Console.WriteLine("      Normally, file names are prepended with the bundle's name.");
            Console.WriteLine("      Note: these names are not compatible with batchimport.");
            Console.WriteLine("  -kd keep .decomp files. When UABEA opens compressed bundles,");
            Console.WriteLine("      they are decompressed into .decomp files. If you want to");
            Console.WriteLine("      decompress bundles, you can use this flag to keep them");
            Console.WriteLine("      without deleting them.");
            Console.WriteLine("  -fd overwrite old .decomp files.");
            Console.WriteLine("  -md decompress into memory. Doesn't write .decomp files.");
            Console.WriteLine("      -kd and -fd won't do anything with this flag set.");
        }

        private static string GetMainFileName(string[] args)
        {
            for (int i = 1; i < args.Length; i++)
            {
                if (!args[i].StartsWith("-"))
                    return args[i];
            }
            return string.Empty;
        }

        private static string? GetOutputDirectory(string[] args)
        {
            int outIndex = Array.IndexOf(args, "-out");
            if (outIndex != -1 && outIndex + 1 < args.Length)
            {
                return args[outIndex + 1];
            }
            else
            {
                return null;
            }
        }

        private static HashSet<string> GetFlags(string[] args)
        {
            HashSet<string> flags = new HashSet<string>();
            for (int i = 1; i < args.Length; i++)
            {
                if (args[i].StartsWith("-"))
                    flags.Add(args[i]);
            }
            return flags;
        }

        private static AssetBundleFile DecompressBundle(string file, string? decompFile)
        {
            AssetBundleFile bun = new AssetBundleFile();

            Stream fs = File.OpenRead(file);
            bun = CommandLineHandler.ReadAssetBundleFile(decompFile, fs, bun);

            return bun;
        }

        private static AssetBundleFile ReadAssetBundleFile(string? decompFile, Stream fs, AssetBundleFile bun)
        {

            AssetsFileReader r = new AssetsFileReader(fs);

            bun.Read(r);
            if (bun.Header.GetCompressionType() != 0)
            {
                Stream nfs;
                if (decompFile == null)
                    nfs = new MemoryStream();
                else
                    nfs = File.Open(decompFile, FileMode.Create, FileAccess.ReadWrite);

                AssetsFileWriter w = new AssetsFileWriter(nfs);
                bun.Unpack(w);

                nfs.Position = 0;
                fs.Close();

                fs = nfs;
                r = new AssetsFileReader(fs);

                bun = new AssetBundleFile();
                bun.Read(r);
            }
            return bun;
        }

        private static string GetNextBackup(string affectedFilePath)
        {
            for (int i = 0; i < 10000; i++)
            {
                string bakName = $"{affectedFilePath}.bak{i.ToString().PadLeft(4, '0')}";
                if (!File.Exists(bakName))
                {
                    return bakName;
                }
            }

            Console.WriteLine("Too many backups, exiting for your safety.");
            return null;
        }

        private static void ExportBundleFile(string[] args, string file, string? exportDirectory)
        {
            HashSet<string> flags = GetFlags(args);

            string? decompFile = $"{file}.decomp";
            if (flags.Contains("-md"))
                decompFile = null;

            if (!File.Exists(file))
            {
                Console.Error.WriteLine($"File {file} does not exist!");
                return;
            }

            DetectedFileType fileType = FileTypeDetector.DetectFileType(file);
            if (fileType != DetectedFileType.BundleFile)
            {
                return;
            }

            AssetBundleFile bun = DecompressBundle(file, decompFile);

            var am = new AssetsManager();

            string classDataPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "classdata.tpk");
            if (File.Exists(classDataPath))
            {
                am.LoadClassPackage(classDataPath);
            }

            int entryCount = bun.BlockAndDirInfo.DirectoryInfos.Length;
            
            var inTargetDir = Path.GetDirectoryName(file);

            List<string> uselessCABFiles = new();

            if (exportDirectory != null)
            {
                Directory.CreateDirectory(exportDirectory);
            }

            for (int i = 0; i < entryCount; i++)
            {
                string name = bun.BlockAndDirInfo.DirectoryInfos[i].Name;

                string cabFilePath;
                if (flags.Contains("-keepnames"))
                    cabFilePath = Path.Combine(inTargetDir, name);
                else
                    cabFilePath = Path.Combine(inTargetDir, $"{Path.GetFileName(file)}_{name}");

                var ass = new AssetWorkspace(am, true);

                byte[]? data = BundleHelper.LoadAssetDataFromBundle(bun, i);

                uselessCABFiles.Add(cabFilePath);
                File.WriteAllBytes(cabFilePath, data);

                AssetsFileInstance fileInst;
                try
                {
                    fileInst = am.LoadAssetsFile(cabFilePath, true);
                }
                catch (Exception ex)
                {
                    continue;
                }
                try
                {
                    ass.LoadedFiles.Add(fileInst);
                    string uVer = fileInst.file.Metadata.UnityVersion;
                    if (uVer == "0.0.0" && fileInst.parentBundle != null)
                    {
                        uVer = fileInst.parentBundle.file.Header.EngineVersion;
                    }
                    am.LoadClassDatabaseFromPackage(uVer);
                
                    foreach (AssetFileInfo info in fileInst.file.AssetInfos)
                    {
                        AssetContainer cont = new(info, fileInst);
                        AssetNameUtils.GetDisplayNameFast(ass, cont, false, out var assetName, out var type);
                        if (type != "MonoBehaviour")
                        {
                            continue;
                        }
                        ass.LoadedAssets.Add(cont.AssetId, cont);

                        AssetTypeValueField? baseField = ass.GetBaseField(cont);

                        if (baseField == null) continue;

                        JToken jBaseField = CommandLineHandler.RecurseJsonDump(baseField, false, true);

                        if (exportDirectory != null)
                        {
                            FileStream fs;
                            assetName = assetName.Replace("/", "_");
                            string filePath = Path.Combine(exportDirectory, assetName + ".json");
                            using (fs = File.Open(filePath, FileMode.Create))
                            using (StreamWriter sw = new(fs))
                            {
                                sw.Write(jBaseField.ToString());
                                //AssetImportExport dumper = new();
                                //dumper.DumpJsonAsset(sw, baseField);
                            }
                        }
                        else
                        {
                            Console.Write(jBaseField.ToString());
                        }
                    }
                }
                catch (Exception ex)
                {
                    Console.Error.Write(ex);
                }
                finally
                {
                    ass = null;
                    am.UnloadAssetsFile(cabFilePath);
                }
            }

            bun.Close();

            am.UnloadAll(true);

            if (!flags.Contains("-kd") && !flags.Contains("-md") && File.Exists(decompFile))
                File.Delete(decompFile);

            GC.Collect();
            GC.WaitForPendingFinalizers();

            foreach (var cabFile in uselessCABFiles)
            {
                try
                {
                    File.Delete(cabFile);
                }
                catch (Exception ex)
                {
                    Console.Error.WriteLine($"Failed to delete CAB file {cabFile}: {ex.Message}");
                }

            }
        }

        private static void BatchExportBundle(string[] args)
        {
            string argPath = GetMainFileName(args);
            FileAttributes attr = File.GetAttributes(argPath);
            string? exportDirectory = GetOutputDirectory(args);

            if ((attr & FileAttributes.Directory) == FileAttributes.Directory)
            { 
                //export all file in directory
                foreach (string file in Directory.EnumerateFiles(argPath))
                {
                    ExportBundleFile(args, file, exportDirectory);
                }
            } 
            else
            {
                // export file
                //exportDirectory = Path.GetDirectoryName(argPath);
                ExportBundleFile(args, argPath, exportDirectory);
            }
        }


        public static JToken RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor,bool isFirst=false)
        {
            AssetTypeTemplateField template = field.TemplateField;

            bool isArray = template.IsArray;

            if (isArray)
            {
                JArray jArray = new();

                if (template.ValueType != AssetValueType.ByteArray)
                {
                    for (int i = 0; i < field.Children.Count; i++)
                    {
                        jArray.Add(RecurseJsonDump(field.Children[i], uabeFlavor));
                    }
                }
                else
                {
                    byte[] byteArrayData = field.AsByteArray;
                    for (int i = 0; i < byteArrayData.Length; i++)
                    {
                        jArray.Add(byteArrayData[i]);
                    }
                }

                return jArray;
            }

            if (field.Value == null)
            {
                JObject jObject = new();

                JArray values = new();
                JArray keys = new();

                List<string> excludedFields = new List<string> { "m_GameObject", "m_Enabled", "m_Script", "m_Name", "objectsById" };

                int countNoExcludedFields = field.Where(p => !excludedFields.Contains(p.FieldName)).Count();

                foreach (AssetTypeValueField child in field)
                {
                    if (isFirst)
                    {   
                        if (excludedFields.Contains(child.FieldName)) continue;
                        if (child.FieldName == "references" && countNoExcludedFields == 1)
                        {
                            // si references est le seul field, dump direct le contenu
                            return RecurseJsonDump(child, uabeFlavor);
                        }
                    }
                    if (child.FieldName == "m_keys")
                    {
                        foreach (AssetTypeValueField subChildKey in child["Array"].Children)
                        {
                            keys.Add(RecurseJsonDump(subChildKey, uabeFlavor));
                        }
                        continue;
                    }
                    if (child.FieldName == "m_values")
                    {
                        foreach (AssetTypeValueField subChildKey in child["Array"].Children)
                        {
                            values.Add(RecurseJsonDump(subChildKey, uabeFlavor));
                        }
                        continue;
                    }

                    if (child.FieldName == "Array")
                    {
                        return RecurseJsonDump(child, uabeFlavor);
                    }
                    else
                    {
                        jObject.Add(child.FieldName, RecurseJsonDump(child, uabeFlavor));
                    }
                }

                if (keys.Count > 0)
                {
                    JObject dictKeyValue = new JObject();
                    for (int i = 0; i < keys.Count;i++)
                    {
                        dictKeyValue.Add(keys[i].ToString(), values[i]);
                    }
                    return dictKeyValue;
                }

                return jObject;
            }
            
            AssetValueType evt = field.Value.ValueType;

            if (field.Value.ValueType != AssetValueType.ManagedReferencesRegistry)
            {
                object value = evt switch
                {
                    AssetValueType.Bool => field.AsBool,
                    AssetValueType.Int8 or
                    AssetValueType.Int16 or
                    AssetValueType.Int32 => field.AsInt,
                    AssetValueType.Int64 => field.AsLong,
                    AssetValueType.UInt8 or
                    AssetValueType.UInt16 or
                    AssetValueType.UInt32 => field.AsUInt,
                    AssetValueType.UInt64 => field.AsULong,
                    AssetValueType.String => field.AsString,
                    AssetValueType.Float => field.AsFloat,
                    AssetValueType.Double => field.AsDouble,
                    _ => "invalid value"
                };

                return (JValue)JToken.FromObject(value);
            }
            else
            { 
                // todo separate method
                ManagedReferencesRegistry registry = field.Value.AsManagedReferencesRegistry;

                if (registry.version == 1 || registry.version == 2)
                {
                    JArray jArrayRefs = new();

                    foreach (AssetTypeReferencedObject refObj in registry.references)
                    {
                        JObject jObjData = new();

                        foreach (AssetTypeValueField child in refObj.data)
                        {
                            jObjData.Add(child.FieldName, RecurseJsonDump(child, uabeFlavor));
                        }

                        jArrayRefs.Add(jObjData);
                    }

                    return jArrayRefs;
                }
                else
                {
                    throw new NotSupportedException($"Registry version {registry.version} not supported!");
                }
            }
        }


        private static void BatchImportBundle(string[] args)
        {
            string importDirectory = GetMainFileName(args);
            if (!Directory.Exists(importDirectory))
            {
                Console.WriteLine("Directory does not exist!");
                return;
            }

            HashSet<string> flags = GetFlags(args);
            foreach (string file in Directory.EnumerateFiles(importDirectory))
            {
                string decompFile = $"{file}.decomp";

                if (flags.Contains("-md"))
                    decompFile = null;

                if (!File.Exists(file))
                {
                    Console.WriteLine($"File {file} does not exist!");
                    return;
                }

                DetectedFileType fileType = FileTypeDetector.DetectFileType(file);
                if (fileType != DetectedFileType.BundleFile)
                {
                    continue;
                }

                Console.WriteLine($"Decompressing {file} to {decompFile}...");
                AssetBundleFile bun = DecompressBundle(file, decompFile);

                List<BundleReplacer> reps = new List<BundleReplacer>();
                List<Stream> streams = new List<Stream>();

                int entryCount = bun.BlockAndDirInfo.DirectoryInfos.Length;
                for (int i = 0; i < entryCount; i++)
                {
                    string name = bun.BlockAndDirInfo.DirectoryInfos[i].Name;
                    string matchName = Path.Combine(importDirectory, $"{Path.GetFileName(file)}_{name}");

                    if (File.Exists(matchName))
                    {
                        FileStream fs = File.OpenRead(matchName);
                        long length = fs.Length;
                        reps.Add(new BundleReplacerFromStream(name, name, true, fs, 0, length));
                        streams.Add(fs);
                        Console.WriteLine($"Importing {matchName}...");
                    }
                }

                //I guess uabe always writes to .decomp even if
                //the bundle is already decompressed, that way
                //here it can be used as a temporary file. for
                //now I'll write to memory since having a .decomp
                //file isn't guaranteed here
                byte[] data;
                using (MemoryStream ms = new MemoryStream())
                using (AssetsFileWriter w = new AssetsFileWriter(ms))
                {
                    bun.Write(w, reps);
                    data = ms.ToArray();
                }
                Console.WriteLine($"Writing changes to {file}...");

                //uabe doesn't seem to compress here

                foreach (Stream stream in streams)
                    stream.Close();

                bun.Close();

                File.WriteAllBytes(file, data);

                if (!flags.Contains("-kd") && !flags.Contains("-md") && File.Exists(decompFile))
                    File.Delete(decompFile);

                Console.WriteLine("Done.");
            }
        }
        
        private static void ApplyEmip(string[] args)
        {
            HashSet<string> flags = GetFlags(args);
            string emipFile = args[1];
            string rootDir = args[2];

            if (!File.Exists(emipFile))
            {
                Console.WriteLine($"File {emipFile} does not exist!");
                return;
            }

            InstallerPackageFile instPkg = new InstallerPackageFile();
            FileStream fs = File.OpenRead(emipFile);
            AssetsFileReader r = new AssetsFileReader(fs);
            instPkg.Read(r, true);

            Console.WriteLine($"Installing emip...");
            Console.WriteLine($"{instPkg.modName} by {instPkg.modCreators}");
            Console.WriteLine(instPkg.modDescription);

            foreach (var affectedFile in instPkg.affectedFiles)
            {
                string affectedFileName = Path.GetFileName(affectedFile.path);
                string affectedFilePath = Path.Combine(rootDir, affectedFile.path);

                if (affectedFile.isBundle)
                {
                    string decompFile = $"{affectedFilePath}.decomp";
                    string modFile = $"{affectedFilePath}.mod";
                    string bakFile = GetNextBackup(affectedFilePath);

                    if (bakFile == null)
                        return;

                    if (flags.Contains("-md"))
                        decompFile = null;

                    Console.WriteLine($"Decompressing {affectedFileName} to {decompFile??"memory"}...");
                    AssetBundleFile bun = DecompressBundle(affectedFilePath, decompFile);
                    List<BundleReplacer> reps = new List<BundleReplacer>();

                    foreach (var rep in affectedFile.replacers)
                    {
                        var bunRep = (BundleReplacer)rep;
                        if (bunRep is BundleReplacerFromAssets)
                        {
                            //read in assets files from the bundle for replacers that need them
                            string assetName = bunRep.GetOriginalEntryName();
                            var bunRepInf = BundleHelper.GetDirInfo(bun, assetName);
                            long pos = bunRepInf.Offset;
                            bunRep.Init(bun.DataReader, pos, bunRepInf.DecompressedSize);
                        }
                        reps.Add(bunRep);
                    }

                    Console.WriteLine($"Writing {modFile}...");
                    FileStream mfs = File.Open(modFile, FileMode.Create);
                    AssetsFileWriter mw = new AssetsFileWriter(mfs);
                    bun.Write(mw, reps, instPkg.addedTypes); //addedTypes does nothing atm
                    
                    mfs.Close();
                    bun.Close();

                    Console.WriteLine($"Swapping mod file...");
                    File.Move(affectedFilePath, bakFile);
                    File.Move(modFile, affectedFilePath);
                    
                    if (!flags.Contains("-kd") && !flags.Contains("-md") && File.Exists(decompFile))
                        File.Delete(decompFile);

                    Console.WriteLine($"Done.");
                }
                else //isAssetsFile
                {
                    string modFile = $"{affectedFilePath}.mod";
                    string bakFile = GetNextBackup(affectedFilePath);

                    if (bakFile == null)
                        return;

                    FileStream afs = File.OpenRead(affectedFilePath);
                    AssetsFileReader ar = new AssetsFileReader(afs);
                    AssetsFile assets = new AssetsFile();
                    assets.Read(ar);
                    List<AssetsReplacer> reps = new List<AssetsReplacer>();

                    foreach (var rep in affectedFile.replacers)
                    {
                        var assetsReplacer = (AssetsReplacer)rep;
                        reps.Add(assetsReplacer);
                    }

                    Console.WriteLine($"Writing {modFile}...");
                    FileStream mfs = File.Open(modFile, FileMode.Create);
                    AssetsFileWriter mw = new AssetsFileWriter(mfs);
                    assets.Write(mw, 0, reps, instPkg.addedTypes);

                    mfs.Close();
                    ar.Close();

                    Console.WriteLine($"Swapping mod file...");
                    File.Move(affectedFilePath, bakFile);
                    File.Move(modFile, affectedFilePath);

                    Console.WriteLine($"Done.");
                }
            }

            return;
        }

        public static void CLHMain(string[] args)
        {
            /*BatchExportBundle(new []
            {
                "batchexportbundle",
                "-md",
                @"C:\Users\Alpa\AppData\Local\Ankama\Dofus-beta\Dofus_Data\StreamingAssets\Content\Map"
            });*/
            
            if (args.Length < 2)
            {
                PrintHelp();
                return;
            }
            
            string command = args[0];

            if (command == "batchexportbundle")
            {
                BatchExportBundle(args);
            }
            else if (command == "batchimportbundle")
            {
                BatchImportBundle(args);
            }
            else if (command == "applyemip")
            {
                ApplyEmip(args);
            }
        }
    }
}