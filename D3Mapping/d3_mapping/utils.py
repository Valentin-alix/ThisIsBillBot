import re
import socket
from typing import Annotated

from pydantic import Field, validate_call


Percentage = Annotated[float, Field(ge=0, le=1.0000001)]


@validate_call
def set_percentage(value: Percentage) -> float:
    return min(value, 1)


def to_snake_case(value: str):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", value).lower()


def get_local_ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as Socket:
        Socket.connect(("8.8.8.8", 80))
        return Socket.getsockname()[0]
