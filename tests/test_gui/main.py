import sys

from tests.test_gui.watcher_window import WatcherGui

if __name__ == "__main__":
    import threading

    watcher_gui = WatcherGui()
    watcher_thread = threading.Thread(target=watcher_gui.watch_files, daemon=True)
    watcher_thread.start()
    sys.exit(watcher_gui.app.exec())
