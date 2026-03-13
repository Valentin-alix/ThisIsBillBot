import random
import secrets
import string

from ankama_launcher_emulator.web.auth.models import RegistrationIdentity

DEFAULT_PASSWORD = "blibli44700"
NICKNAME_MIN_LENGTH = 8
NICKNAME_MAX_LENGTH = 14
NICKNAME_ALPHABET = string.ascii_letters

FIRST_NAMES = [
    "Alphonse",
    "Benoit",
    "Cyril",
    "David",
    "Emmanuel",
    "Franck",
    "Gilles",
    "Hugo",
    "Igor",
    "Jules",
    "Karl",
    "Lucas",
    "Maurice",
    "Nicolas",
    "Olivier",
    "Pierre",
    "Quentin",
    "Romain",
    "Sylvain",
    "Thibault",
    "Ulysse",
    "Victor",
    "William",
    "Xavier",
    "Yann",
    "Zacharie",
]
LAST_NAMES = [
    "Teston",
    "Dupont",
    "Durand",
    "Martin",
    "Bernard",
    "Dubois",
    "Thomas",
    "Robert",
    "Richard",
    "Petit",
    "Leroy",
    "Moreau",
    "Simon",
    "Laurent",
    "Lefevre",
    "Michel",
    "Garcia",
    "David",
    "Bertrand",
    "Roux",
    "Vincent",
    "Fournier",
    "Morel",
    "Girard",
    "Andre",
]


def random_identity() -> RegistrationIdentity:
    return RegistrationIdentity(
        firstname=random.choice(FIRST_NAMES),
        lastname=random.choice(LAST_NAMES),
        birthday_day=f"{random.randint(1, 27):02d}",
        birthday_month=f"{random.randint(1, 11):02d}",
        birthday_year=str(random.randint(1950, 1999)),
    )


def generate_nickname() -> str:
    length = random.randint(NICKNAME_MIN_LENGTH, NICKNAME_MAX_LENGTH)
    first_character = secrets.choice(string.ascii_uppercase)
    remaining_characters = (
        "".join(secrets.choice(NICKNAME_ALPHABET) for _index in range(length - 1))
    ).lower()
    return first_character + remaining_characters
