## Project Overview

**DBDofusUnity** has two independent pipelines:
1. **Data extraction** (`dofus_unity_reader/`) - pulls game assets from Unity bundles via UABEA
2. **Protocol mapping** (`proto_mapper_assembly/`) - maps obfuscated C# protobuf messages to non-obfuscated equivalents, writes `datas/protos/game_mappings.json`
