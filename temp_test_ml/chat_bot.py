import os
from pathlib import Path

from dotenv import load_dotenv

from src.core.logic.chat.chat_bot import get_human_response_to_private_msg

load_dotenv(os.path.join(Path(__file__).parent.parent, ".env"))


if __name__ == "__main__":
    print(get_human_response_to_private_msg("ok ca marche mec"))
