import os
from pathlib import Path

from dotenv import load_dotenv

from src.core.logic.chat.human_response import HumanResponse

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))


if __name__ == "__main__":
    real_human_name = "cemec"
    bot_name = "cebot"
    print(
        HumanResponse().get_human_response_to_private_msg(
            "yo", real_human_name, bot_name
        )
    )
