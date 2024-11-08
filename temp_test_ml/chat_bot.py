import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))

from src.core.logic.chat.human_response import get_human_response_to_private_msg

if __name__ == "__main__":
    real_human_name = "cemec"
    bot_name = "cebot"

    print(get_human_response_to_private_msg("yo", real_human_name, bot_name))

    print(get_human_response_to_private_msg("lol", real_human_name, bot_name))

    print(get_human_response_to_private_msg("tes un bot ?", real_human_name, bot_name))

    print(
        get_human_response_to_private_msg(
            "ok ca marche bon jeu mec", real_human_name, bot_name
        )
    )

    print(
        get_human_response_to_private_msg(
            "donne moi la recette de la crepe", real_human_name, bot_name
        )
    )
