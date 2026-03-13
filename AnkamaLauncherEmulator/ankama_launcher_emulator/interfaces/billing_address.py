import random

from pydantic import BaseModel, ConfigDict

_FIRST_NAMES = [
    "Lucas",
    "Emma",
    "Louis",
    "Chloe",
    "Hugo",
    "Manon",
    "Nathan",
    "Camille",
    "Thomas",
    "Sarah",
]
_LAST_NAMES = [
    "Martin",
    "Bernard",
    "Dubois",
    "Thomas",
    "Robert",
    "Petit",
    "Durand",
    "Leroy",
    "Moreau",
    "Simon",
]
_STREET_TYPES = ["rue", "avenue", "boulevard", "impasse", "chemin"]
_STREET_NAMES = [
    "de la Paix",
    "des Lilas",
    "Victor Hugo",
    "de la Republique",
    "des Fleurs",
    "du Moulin",
    "de la Gare",
    "des Ecoles",
]
_CITIES_BY_ZIPCODE = {
    "75001": "Paris",
    "69001": "Lyon",
    "13001": "Marseille",
    "31000": "Toulouse",
    "44000": "Nantes",
    "67000": "Strasbourg",
    "59000": "Lille",
    "33000": "Bordeaux",
}


class BillingAddressInfo(BaseModel):
    model_config = ConfigDict(extra="forbid")

    firstname: str
    lastname: str
    address: str
    zipcode: str
    city: str


def generate_random_billing_address(login: str) -> BillingAddressInfo:
    rng = random.Random(login)
    zipcode = rng.choice(list(_CITIES_BY_ZIPCODE))
    return BillingAddressInfo(
        firstname=rng.choice(_FIRST_NAMES),
        lastname=rng.choice(_LAST_NAMES),
        address=f"{rng.randint(1, 150)} {rng.choice(_STREET_TYPES)} {rng.choice(_STREET_NAMES)}",
        zipcode=zipcode,
        city=_CITIES_BY_ZIPCODE[zipcode],
    )
