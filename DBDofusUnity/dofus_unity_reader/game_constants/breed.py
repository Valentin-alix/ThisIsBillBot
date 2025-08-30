from enum import IntEnum

from datas.protos.non_obf.connection.login_message_pb2 import CharacterInformation

Breed = CharacterInformation.Breed


class BreedEnum(IntEnum):
    SACRIER = Breed.SACRIER + 1
    IOP = Breed.IOP + 1
    CRA = Breed.CRA + 1
    XELOR = Breed.XELOR + 1


DEFAULT_SACRIEUR_COSMETIC_ID = 169
