import os
from pathlib import Path

RESOURCE_FOLDER = os.path.join(Path(__file__).parent.parent.parent, "resources")

DESCRIPTOR_FOLDER = os.path.join(RESOURCE_FOLDER, "descriptors")
PROTO_FOLDER = os.path.join(RESOURCE_FOLDER, "proto")
