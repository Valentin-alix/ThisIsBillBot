# Web-flow debugging

- Before changing a failing registration, authentication, or subscription flow, inspect the relevant Playwright trace when it can clarify the failure. Use Trace Viewer on `resources/debug/traces/<timestamp>_<login>/trace.zip` and correlate navigation, requests, and page state with logs and owning code.
- Traces contain sensitive account data; do not paste raw contents or secrets into reports.
- Do not repeat a live registration or purchase solely to create a trace without explicit authorization.
