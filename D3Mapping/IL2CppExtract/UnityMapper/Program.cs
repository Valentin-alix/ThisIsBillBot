using System.Text;
using System.Text.Json;
using System.IO;
using System.Net.Http.Headers;
/*
 * Ce script lit deux fichiers :
 *  - Classes.json : liste ordonnée des noms de classes du protocole (JSON),
 *  - Types.bin    : données binaires contenant les chaînes statiques de types.
 *
 * Il parcourt Types.bin via un BinaryReader :
 * 1) Ignore un Int32
 * 2) Lit un octet (longueur du nom),
 * 3) Lit cette longueur d’octets et décode en UTF-8 pour obtenir "Namespace|NomDeClasse".
 *
 * Chaque type est filtré (exclusion des noms terminant par |Types ou contenant +Types),
 * puis regroupé par "vrai namespace" extrait après ".Protocol" ou ".Protocol.Connection".
 *
 * Ensuite, les classes sont divisées en sous-groupes à chaque occurrence d’un nom se terminant
 * par "Reflection", afin de conserver l’ordre logique des sous-ensembles.
 *
 * Pour chaque sous-groupe dans l’ordre, on aligne les noms extraits du binaire
 * avec la portion correspondante dans la liste JSON (offset cumulatif).
 * Cette correspondance est stockée dans un dictionnaire globalMapping :
 *   Clé   = nom de classe JSON
 *   Valeur= "Namespace|NomDeClasseBinaire"
 *
 * Enfin, on renverse l’ordre des paires et on écrit globalMapping dans
 * Mapping.json (format JSON indenté).
 *
 * Le résultat permet de créer un fichier Mapping.json qui relie la définition
 * haute-niveau des messages du protocole à leur nom effectif dans l’assembly compilé.
 */


class Program
{
    static async Task Main(string[] args)
    {
        string currentDirectory = Directory.GetCurrentDirectory();
        string parentDirectory = Directory.GetParent(currentDirectory)!.FullName;
        string il2CppExtractOuput = Path.Combine(parentDirectory, "IL2CppExtract", "Output");
        string connectionProtocol = Path.Combine(il2CppExtractOuput, "Ankama.Dofus.Protocol.Connection");
        string gameProtocol = Path.Combine(il2CppExtractOuput, "Ankama.Dofus.Protocol.Game");
        await Mapping.MapByClassesAndTypes(classPath: Path.Combine(connectionProtocol, "Classes.json"), typesPath: Path.Combine(connectionProtocol, "Types.bin"), output: "ConnectionMapping.json");
        await Mapping.MapByClassesAndTypes(classPath: Path.Combine(gameProtocol, "Classes.json"), typesPath: Path.Combine(gameProtocol, "Types.bin"), output: "GameMapping.json");
    }
}

public class Mapping
{
    public async static Task MapByClassesAndTypes(string classPath, string typesPath, string output)
    {
        // Les classes du protocol dans l'ordre du binary
        var classes = JsonSerializer.Deserialize<List<string>>(await File.ReadAllTextAsync(classPath))!;
        // Le RVA Field static des strings du binary
        var typesBin = await File.ReadAllBytesAsync(typesPath);

        classes.Reverse();

        var nss = new Dictionary<string, List<string>>();

        // get all namespaces with their all respective type inside
        var binaryReader = new BinaryReader(new MemoryStream(typesBin));
        while (binaryReader.BaseStream.Position < binaryReader.BaseStream.Length)
        {
            binaryReader.ReadInt32();
            var typeLen = binaryReader.ReadByte();
            var type = Encoding.UTF8.GetString(binaryReader.ReadBytes(typeLen));

            // En vrai, on pourrait prendre ça en compte plus tard
            if (type.EndsWith("|Types") || type.Contains("+Types"))
            {
                continue;
            }

            var namspc = type.Split('|')[0];
            var _type = type.Split('|')[1];

            string realNs;

            if (namspc.Contains(".Server.Connection"))
            {
                if (namspc.Contains(".Protocol") == false)
                    continue;

                realNs = namspc.Split(".Protocol")[1];
            }
            else
            {
                // we get every string after .Protocol 
                if (namspc.Contains(".Protocol.") == false)
                    continue;

                realNs = namspc.Split(".Protocol.")[1];
            }

            if (realNs.Contains('.') && nss.ContainsKey(realNs.Split('.')[0]))
            {
                realNs = realNs.Split('.')[0];
            }

            if (!nss.TryGetValue(realNs, out var value))
            {
                value = [];
                nss[realNs] = value;
            }

            value.Add(_type);
        }

        var globalGroups = new Dictionary<string, List<string>>();
        var currentGroup = string.Empty; // current group (get from reflection classe)

        // iterate throught all namespaces & put by namespaces name by reflection name the types insides
        foreach (var ns in nss)
        {
            // construct by reflection name the types inside
            var group = new Dictionary<string, List<string>>();
            foreach (var type in ns.Value)
            {
                var isReflection = type.EndsWith("Reflection");

                if (isReflection)
                {
                    currentGroup = type;
                }

                if (!group.TryGetValue(currentGroup, out var value))
                {
                    value = [];
                    group[currentGroup] = value;
                }

                value.Add(type);
            }

            // on reverse le group (jsp pk) avant de le mettre dans globalGroups
            var reversedGroup = group.Reverse();
            foreach (var g in reversedGroup)
            {
                if (globalGroups.TryGetValue(g.Key, out var value))
                {
                    value.AddRange(g.Value);
                    continue;
                }

                globalGroups[g.Key] = g.Value;
            }
        }

        var offset = 0;

        var globalMapping = new Dictionary<string, string>();

        foreach (var reverseOrder in globalGroups.Select(g => g.Value))
        {
            reverseOrder.Reverse();

            var count = reverseOrder.Count;

            var classOfThis = classes.Skip(offset).Take(count).ToList();

            for (var i = 0; i < count; i++)
            {
                //Console.WriteLine(classOfThis[i]);
                globalMapping[classOfThis[i]] = reverseOrder[i];
            }

            offset += count;
        }
        // reverse the dictionary order
        globalMapping = globalMapping.Reverse().ToDictionary(x => x.Key, x => x.Value);
        await File.WriteAllTextAsync(output, JsonSerializer.Serialize(globalMapping, new JsonSerializerOptions { WriteIndented = true }));
    }
}
