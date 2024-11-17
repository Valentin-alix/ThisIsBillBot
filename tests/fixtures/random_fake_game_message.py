from google.protobuf.message import Message

from tests.fixtures.random_proto_generators import (
    generate_CharacterSelectionEvent,
    generate_MapComplementaryInformationEvent,
    generate_MapCurrentEvent,
    generate_ObjectAddedEvent,
)


def generate_new_map_msgs():
    map_current_event = generate_MapCurrentEvent()
    return [
        map_current_event,
        generate_MapComplementaryInformationEvent(map_id=map_current_event.map_id),
    ]


def generate_random_fake_game_message() -> list[Message]:
    msgs = [
        generate_CharacterSelectionEvent(),
        *[generate_ObjectAddedEvent() for _ in range(100)],
    ]
    for _ in range(3):
        msgs.extend(generate_new_map_msgs())
    return msgs


if __name__ == "__main__":
    for _ in range(50):
        generate_ObjectAddedEvent()
