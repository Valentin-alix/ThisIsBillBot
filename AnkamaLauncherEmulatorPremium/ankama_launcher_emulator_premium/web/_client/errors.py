class WebError(RuntimeError):
    """Root of all web-pipeline failures (auth, store, paysafecard, ...)."""
