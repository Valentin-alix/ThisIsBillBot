## Architecture Notes

- Emulates Ankama Launcher via Thrift server on port **26116** (game connects here, not real launcher).
- Reads/decrypts existing credentials from `BOTS_STORAGE_PATH`.
- `cytrus-v6` (npm) optional; enables in-app game updates when present. Detected via `shutil.which()`.

## Web-flow debugging

For registration, authentication, or subscription failures, inspect the relevant Playwright trace before changing the web flow when it can clarify the failure. Traces are written to `resources/debug/traces/<timestamp>_<login>/trace.zip`; use the Playwright Trace Viewer and correlate the observed navigation, requests, and page state with the logs and the owning code. These archives can contain sensitive account data: do not paste their contents into reports, and do not repeat a live registration or purchase solely to create a trace without explicit authorization.
