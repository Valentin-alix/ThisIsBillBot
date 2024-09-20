## Requirements

- python >=3.10
- protoc-28.0 : https://github.com/protocolbuffers/protobuf/releases/download/v28.0/protoc-28.0-win64.zip (depending on your os)
- launch init.sh

## How to use

Activate the virtual environment
- `poetry shell`

### Sniffer

(FIXME There is a bug for certain message, somehow only for the sniffer ?)
- `python src/sniffer.py`

### Mitm

- Launch redirect.py from https://github.com/Valentin-alix/Mitm-Http.git
- Create localhost proxy at port 8080 (Check on google how to do that for your computer)
- `python src/mitm/listener.py`


## Generator

### Proto
`python ./scripts/generator/generate_proto_from_descriptor.py`

### Python protobuf message

`python ./scripts/generator/generate_python_from_proto.py`

