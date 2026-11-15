import os

from google.adk.models import Gemini
from google.genai import types

# Change models in one place (or set FIELDKIT_MODEL in .env).
MODEL_NAME = os.environ.get("FIELDKIT_MODEL", "gemini-3.5-flash")

# Gemini sometimes returns 503 "high demand" or 429 "rate limited".
# Retry with exponential backoff instead of failing the whole question.
MODEL = Gemini(
    model=MODEL_NAME,
    retry_options=types.HttpRetryOptions(
        attempts=5,            # try up to 5 times
        initial_delay=2,       # wait 2s, then 4s, 8s... (capped below)
        max_delay=30,
        http_status_codes=[429, 500, 503],
    ),
)
