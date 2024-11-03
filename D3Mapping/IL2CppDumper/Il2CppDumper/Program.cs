using System;
using System.IO;
using System.Linq;
using System.Runtime.InteropServices;
using System.Text.Json;

namespace Il2CppDumper
{
    class Program
    {
        private static Config config;

        [STAThread]
        static void Main(string[] args)
        {
            config = JsonSerializer.Deserialize<Config>(File.ReadAllText(AppDomain.CurrentDomain.BaseDirectory + @"config.json"));
            string il2cppPath = null;
            string metadataPath = null;
            string outputDir = null;

            if (args.Length == 1)
            {
                if (args[0] == "-h" || args[0] == "--help" || args[0] == "/?" || args[0] == "/h")
                {
                    ShowHelp();
                    return;
                }
            }
            if (args.Length > 3)
            {
                ShowHelp();
                return;
            }
            if (args.Length > 1)
            {
                foreach (var arg in args)
                {
                    if (File.Exists(arg))
                    {
                        var file = File.ReadAllBytes(arg);
                        if (BitConverter.ToUInt32(file, 0) == 0xFAB11BAF)
                        {
                            metadataPath = arg;
                        }
                        else
                        {
                            il2cppPath = arg;
                        }
                    }
                    else if (Directory.Exists(arg))
                    {
                        outputDir = Path.GetFullPath(arg) + Path.DirectorySeparatorChar;
                    }
                }
            }
            outputDir ??= AppDomain.CurrentDomain.BaseDirectory;
            if (RuntimeInformation.IsOSPlatform(OSPlatform.Windows))
            {
                if (il2cppPath == null)
                {
                    var ofd = new OpenFileDialog
                    {
                        Filter = "Il2Cpp binary file|*.*"
                    };
                    if (ofd.ShowDialog())
                    {
                        il2cppPath = ofd.FileName;
                        ofd.Filter = "global-metadata|global-metadata.dat";
                        if (ofd.ShowDialog())
                        {
                            metadataPath = ofd.FileName;
                        }
                        else
                        {
                            return;
                        }
                    }
                    else
                    {
                        return;
                    }
                }
            }
            if (il2cppPath == null)
            {
                ShowHelp();
                return;
            }
            if (metadataPath == null)
            {
                Console.WriteLine($"ERROR: Metadata file not found or encrypted.");
            }
            else
            {
                try
                {
                    if (Il2CppParser.Init(il2cppPath, metadataPath, out var metadata, out var il2Cpp))
                    {
                        Dump(metadata, il2Cpp, outputDir);
                    }
                }
                catch (Exception e)
                {
                    Console.WriteLine(e);
                }
            }
            if (config.RequireAnyKey)
            {
                Console.WriteLine("Press any key to exit...");
                Console.ReadKey(true);
            }
        }

        static void ShowHelp()
        {
            Console.WriteLine($"usage: {AppDomain.CurrentDomain.FriendlyName} <executable-file> <global-metadata> <output-directory>");
        }

        private static void Dump(Metadata metadata, Il2Cpp il2Cpp, string outputDir)
        {
            Console.WriteLine("Dumping...");
            var executor = new Il2CppExecutor(metadata, il2Cpp);
            var decompiler = new Il2CppDecompiler(executor);
            decompiler.Decompile(config, outputDir);
            Console.WriteLine("Done!");
            if (config.GenerateStruct)
            {
                Console.WriteLine("Generate struct...");
                var scriptGenerator = new StructGenerator(executor);
                scriptGenerator.WriteScript(outputDir);
                Console.WriteLine("Done!");
            }
            if (config.GenerateDummyDll)
            {
                Console.WriteLine("Generate dummy dll...");
                DummyAssemblyExporter.Export(executor, outputDir, config.DummyDllAddToken);
                Console.WriteLine("Done!");
            }
        }
    }
}
