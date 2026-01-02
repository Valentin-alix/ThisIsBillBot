---
name: ankama-web-debugging
description: Diagnose Ankama web registration, authentication, or subscription failures using the local Playwright traces, logs, and owning code.
---

# Ankama web-flow debugging

Use this for a failure in the Playwright-backed registration, authentication, or subscription flows of `AnkamaLauncherEmulatorPremium`.

## Evidence

The browser client writes one archive per run to
`AnkamaLauncherEmulatorPremium/resources/debug/traces/<timestamp>_<login>/trace.zip`.
Select the trace matching the affected account and time window, then inspect it with the Playwright Trace Viewer. Correlate its navigation, requests, DOM snapshots, and screenshots with the application logs and the owning flow before proposing a code change.

Do not infer that an empty traces directory disproves the incident: traces are generated only by a browser run and the debug directory is ignored by Git. Do not rerun a registration or subscription merely to create a trace without the user's explicit authorization.

## Reporting

State which trace and time window support the diagnosis, distinguish a site/provider response from an automation defect, and cite the relevant source path. Treat trace archives as sensitive: do not copy credentials, tokens, confirmation codes, or full request payloads into the report.
