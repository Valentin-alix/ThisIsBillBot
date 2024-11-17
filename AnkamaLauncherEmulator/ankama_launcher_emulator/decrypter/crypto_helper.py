import base64
import getpass
import hashlib
import json
import os
from typing import Any

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from ankama_launcher_emulator.consts import (
    API_KEY_FOLDER_PATH,
    CERTIFICATE_FOLDER_PATH,
)
from ankama_launcher_emulator.decrypter.device import Device
from ankama_launcher_emulator.interfaces.deciphered_api_key import (
    DecipheredApiKey,
    DecipheredApiKeyDatas,
)
from ankama_launcher_emulator.interfaces.deciphered_cert import (
    DecipheredCertifDatas,
    StoredCertificate,
)


class CryptoHelper:
    @staticmethod
    def getStoredCertificate(login: str) -> StoredCertificate:
        file_path = os.path.join(
            CERTIFICATE_FOLDER_PATH,
            ".certif" + CryptoHelper.createHashFromStringSha(login),
        )
        return {
            "certificate": CryptoHelper.decryptFromFileWithUUID(file_path),
            "filepath": file_path,
        }

    @staticmethod
    def getStoredApiKeys() -> list[DecipheredApiKey]:
        deciphered_apikeys: list[DecipheredApiKey] = []
        for apikey_file in os.listdir(API_KEY_FOLDER_PATH):
            if not apikey_file.startswith(".key"):
                continue
            apikey_data: DecipheredApiKeyDatas = CryptoHelper.decryptFromFileWithUUID(
                os.path.join(API_KEY_FOLDER_PATH, apikey_file)
            )
            deciphered_apikeys.append(
                {"apikeyFile": apikey_file, "apikey": apikey_data}
            )
        return deciphered_apikeys

    @staticmethod
    def getStoredApiKey(login: str) -> DecipheredApiKey:
        return next(
            deciphered_api_key
            for deciphered_api_key in CryptoHelper.getStoredApiKeys()
            if deciphered_api_key["apikey"]["login"] == login
        )

    @staticmethod
    def decryptFromFileWithUUID(file_path: str):
        uuid = Device.getUUID()
        return CryptoHelper.decryptFromFile(file_path, uuid)

    @staticmethod
    def decryptFromFile(file_path: str, uuid: str):
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        return CryptoHelper.decrypt(data, uuid)

    @staticmethod
    def decrypt(data: str, uuid: str) -> Any:
        splitted_datas = data.split("|")
        iv = bytes.fromhex(splitted_datas[0])
        data_to_decrypt = bytes.fromhex(splitted_datas[1])

        key = CryptoHelper.createHashFromString(uuid)

        decipher = AES.new(key, AES.MODE_CBC, iv)

        decrypted_data = decipher.decrypt(data_to_decrypt)
        decrypted_data = unpad(decrypted_data, AES.block_size)
        return json.loads(decrypted_data.decode("utf-8"))

    @staticmethod
    def encrypt(json_obj: Any, uuid: str) -> str:
        key = CryptoHelper.createHashFromString(uuid)
        iv = os.urandom(16)
        cipher = AES.new(key, AES.MODE_CBC, iv)

        encrypted_data = json.dumps(json_obj).encode("utf-8")
        padded_data = pad(encrypted_data, AES.block_size)

        encrypted_data = cipher.encrypt(padded_data)

        return iv.hex() + "|" + encrypted_data.hex()

    @staticmethod
    def createHashFromStringSha(string: str):
        return hashlib.sha256(string.encode("utf-8")).hexdigest()[:32]

    @staticmethod
    def createHashFromString(string: str):
        return hashlib.md5(string.encode("utf-8")).digest()

    @staticmethod
    def createHmEncoders():
        arch = Device.getArch()
        plt = Device.getPlatform()
        machine_id = Device.getMachineId(plt, arch)
        username = getpass.getuser()
        os_version = Device.getOsVersion()
        ram = Device.getComputerRam()
        machine_infos = [
            arch,
            plt,
            machine_id,
            username,
            str(int(os_version)),
            str(ram),
        ]
        hm1 = CryptoHelper.createHashFromStringSha("".join(machine_infos))
        hm2 = hm1[::-1]
        return hm1, hm2

    @staticmethod
    def generateHashFromCertif(certif: DecipheredCertifDatas):
        hm1, hm2 = CryptoHelper.createHmEncoders()

        decipher = AES.new(hm2.encode(), AES.MODE_ECB)

        decoded_certificate = base64.b64decode(certif["encodedCertificate"])
        decrypted_certificate = decipher.decrypt(decoded_certificate)

        try:
            decrypted_certificate = unpad(decrypted_certificate, AES.block_size)
        except ValueError:
            pass

        combined_datas = hm1.encode() + decrypted_certificate
        return hashlib.sha256(combined_datas).hexdigest()

    @staticmethod
    def encryptToFile(file_path, json_obj, uuid):
        encrypted_json_obj = CryptoHelper.encrypt(json_obj, uuid)
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(encrypted_json_obj)
