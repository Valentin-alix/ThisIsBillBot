# IL2Cpp Reverse-Utility Suite

A small collection of **two** command-line helpers for working with Unity IL2Cpp binaries:

| Tool | Purpose |
|------|---------|
| **`IL2CppExtract`** | Scans an IL2Cpp‐ generated executable or shared library and lists the **RVA** offsets of every field and method it finds. |
| **`UnityMapper`**   | Uses the RVA list to translate **obfuscated class** back to their real names. |

> These tools aim to make reverse-engineering mobile and desktop IL2Cpp games a little less painful.

---

## 📦 Quick start

```bash
# Clone
git clone https://github.com/AlpaGit/IL2CppExtract.git
cd IL2CppExtract

# Change for your configuration
You probabily will need to change the directory of your game folder in the Program.cs

# Build everything (requires .NET 9 SDK)
dotnet build -c Release

```

- Start IL2CppExtract and it will create a Output folder with multiple directory of libaries containing every static fields
- Copy the `Types.bin` and the `Classes.json` from `Output/Ankama.Dofus.Protocol.Game` to the `UnityMapper` tool and it will create a json mapping of the classes
