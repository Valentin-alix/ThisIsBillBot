from threading import Thread
from src.gui.application import launch_gui
from src.core.account.ankama_launcher import AnkamaLauncher
from src.mitm.listener import Listener


def main():
    ankama_launcher = AnkamaLauncher()
    listener = Listener(ankama_launcher.account_by_id)
    Thread(
        target=lambda: listener.start_listener(
            5555, ("dofus2-co-beta.ankama-games.com", 5555), True
        ),
        daemon=True,
    ).start()
    launch_gui(ankama_launcher.account_by_id)


if __name__ == "__main__":
    main()
