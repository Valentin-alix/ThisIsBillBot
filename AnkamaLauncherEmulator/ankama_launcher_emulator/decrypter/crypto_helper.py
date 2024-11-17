import base64
import getpass
import hashlib
import json
import os
from typing import Any

from Cryptodome.Cipher import AES
from Cryptodome.Util.Padding import pad, unpad

from AnkamaLauncherEmulator.ankama_launcher_emulator.consts import (
    API_KEY_FOLDER_PATH,
    CERTIFICATE_FOLDER_PATH,
)
from AnkamaLauncherEmulator.ankama_launcher_emulator.decrypter.device import Device
from AnkamaLauncherEmulator.ankama_launcher_emulator.interfaces.deciphered_api_key import (
    DecipheredApiKey,
    DecipheredApiKeyDatas,
)
from AnkamaLauncherEmulator.ankama_launcher_emulator.interfaces.deciphered_cert import (
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


if __name__ == "__main__":
    datas = CryptoHelper.getStoredApiKey("ezrealeu44700_main@outlook.com")

    temp = {
        "apikeyFile": ".keydata182394599",
        "apikey": {
            "key": "c19494d7-c6a4-49ed-a504-7b582e6e5d91",
            "provider": "ankama",
            "refreshToken": "cf29109b-a71e-4104-9a90-05aa8c2f0180",
            "isStayLoggedIn": True,
            "accountId": 182394599,
            "login": "ezrealeu44700_main@outlook.com",
            "certificate": {
                "id": 522791184,
                "encodedCertificate": "BmlqFSudzq1+8wFBhlz7vW1GtxzGxEXTfM+2Sh+lPr7TpTUezMwQnDPtLqVQ01fGSR++Fsx995gl9hEp49SCq4aw9NwH0gowx7g2w3kJF//ZFE0m4cJegzeP8KsHHXRtZSiOqpUQG/KfWU9URfmEGuM1ya/32ivQBsobPRNpryV2HyC+xF0eJ2Ma3peKH+fDY2zURRF4ZjdbhBiyEF0n0A2Xr2NqtR/Urq9ztUHiXZGQR8KwNQccB3+/ZEBiOl4EQlTgHyrYb5XycLCo2QdM9C9ds+XXFFUzEGWYetL3nAji/C9eVerIkDVx0cB3ZYh/SSadQ0qpGBPSUkZ5+sUIjos1a7qAevz/Ot9i/GkcsyL55Ni4XIF2VkqWY+ck9Y3N/quOn/85gqlOxjfYE+l8rTBngAwT8GlBljm0k1snr0wNgLoUzkhxChK5AENQJ87HfY6/WyTwx5qu88pIgL7bDxFljHTsBzZsaQbK8Gu1LsTS4R+uf5rGLtXpxYmMKgzlQbDD98RYR3/ikoevgtjwDxoF3uKf0FybqmJEVwmT8nCkVAPvQzb7mgCc/2co0J/gGnykMz7bdd3taACrhoTOxAQGMqUUzqmnUpVqw/LdNQ+oVcH/2r7Fay4LR6MZI09z2BDcnGb/fnUuwooiecMNwHYys9qTXmPL6p7Z+p389Ri/pNO1rDFmTI7BW8ueyOc+ecGgeUwf7amIualyBAweQ/RQsOiKgiVVMPQGBCHC8mI7OUiEkYe1U8FtdYWGS31r8moshKKIFX1Iil/HOvStqtWci8ynEEKm02qfWWL/DIt0syrfAaf3CNBazlcP8zDsmAeT5XBGg9R3VHG1w5FYfRoVxUTvjDHBSastfYvdeyeEFREbT1c8A9FIYWdgcklYCfL+ndoMGEJavb6sHtowcQ==",
                "login": "ezrealeu44700_main@outlook.com",
            },
            "refreshDate": 1748523228885,
        },
    }
    yolo = CryptoHelper.encrypt(temp, Device.getUUID())
