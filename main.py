"""
Main entry point for the Blood Test Reference Values API.
"""
import os
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
import uvicorn

# Initialize Sentry SDK
sentry_sdk.init(
    dsn="https://6995265bd39205370b934ee1dc980c15@o4509519455191040.ingest.de.sentry.io/4509519471509584",
    integrations=[
        FastApiIntegration(),
        StarletteIntegration(),
    ],
    # Set traces_sample_rate to 1.0 to capture 100%
    # of transactions for performance monitoring.
    traces_sample_rate=1.0,
    # Set profiles_sample_rate to 1.0 to profile 100%
    # of sampled transactions.
    profiles_sample_rate=1.0,
    environment=os.getenv("ENV", "development"),
    send_default_pii=True,  # Add data like request headers and IP for users
)

from bloodtest_tools.api import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.getenv("PORT", "8001")),  # Default to 8001 if PORT env var not set
        log_level="debug"
    )
