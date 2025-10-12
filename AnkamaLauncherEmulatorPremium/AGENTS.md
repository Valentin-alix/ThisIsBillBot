## Architecture Notes

- Emulates Ankama Launcher via Thrift server on port **26116** (game connects here, not real launcher).
- Reads/decrypts existing credentials from `BOTS_STORAGE_PATH`.
- `cytrus-v6` (npm) optional; enables in-app game updates when present. Detected via `shutil.which()`.