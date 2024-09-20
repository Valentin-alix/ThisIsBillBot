import unittest

from com.ankama.dofus.server.game.protocol.connection_pb2 import IdentificationRequest
from com.ankama.dofus.server.game.protocol_pb2 import Message


class TestSniffer(unittest.TestCase):
    def test_parse_game_msg(self):
        content = bytearray(
            b"\n\x8e\x01\x08\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x12\x80\x01\nVtype.ankama.com/com.ankama.dofus.server.game.protocol.connection.IdentificationRequest\x12&\n f42414ed79cf49eca4481a2066528b7d\x12\x02fr"
        )
        msg = Message()
        msg.ParseFromString(content)

        print(msg.request.content.type_url)
        print(IdentificationRequest.DESCRIPTOR.full_name)

        if msg.request.content.Is(IdentificationRequest.DESCRIPTOR):
            req_msg = IdentificationRequest()
            msg.request.content.Unpack(req_msg)
            print(req_msg.ticket_key)
