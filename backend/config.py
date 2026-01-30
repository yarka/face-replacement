"""
Configuration module for loading environment variables
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Mock mode for testing without real API calls
MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"

# Freepik API
FREEPIK_API_KEY = os.getenv("FREEPIK_API_KEY", "")
FREEPIK_API_BASE_URL = os.getenv("FREEPIK_API_BASE_URL", "https://api.freepik.com/v1/ai/video")
FREEPIK_RUNWAY_BASE_URL = os.getenv("FREEPIK_RUNWAY_BASE_URL", FREEPIK_API_BASE_URL)

# Explicit endpoints (set these for real API)
FREEPIK_RUNWAY_CREATE_URL = os.getenv(
    "FREEPIK_RUNWAY_CREATE_URL",
    f"{FREEPIK_RUNWAY_BASE_URL}/runway-act-two"
)
FREEPIK_RUNWAY_STATUS_URL_TEMPLATE = os.getenv(
    "FREEPIK_RUNWAY_STATUS_URL_TEMPLATE",
    f"{FREEPIK_RUNWAY_BASE_URL}/runway-act-two/{{task_id}}"
)

# Seedream 4 Edit (image editing)
FREEPIK_SEEDREAM_EDIT_CREATE_URL = os.getenv(
    "FREEPIK_SEEDREAM_EDIT_CREATE_URL",
    "https://api.freepik.com/v1/ai/text-to-image/seedream-v4-edit"
)
FREEPIK_SEEDREAM_EDIT_STATUS_URL_TEMPLATE = os.getenv(
    "FREEPIK_SEEDREAM_EDIT_STATUS_URL_TEMPLATE",
    "https://api.freepik.com/v1/ai/text-to-image/seedream-v4-edit/{task_id}"
)

# Kling 2.5 Pro (image-to-video)
FREEPIK_KLING_CREATE_URL = os.getenv(
    "FREEPIK_KLING_CREATE_URL",
    "https://api.freepik.com/v1/ai/image-to-video/kling-v2-5-pro"
)
FREEPIK_KLING_STATUS_URL_TEMPLATE = os.getenv(
    "FREEPIK_KLING_STATUS_URL_TEMPLATE",
    "https://api.freepik.com/v1/ai/image-to-video/kling-v2-5-pro/{task_id}"
)

# Cloudinary
CLOUDINARY_CLOUD_NAME = os.getenv("CLOUDINARY_CLOUD_NAME", "")
CLOUDINARY_API_KEY = os.getenv("CLOUDINARY_API_KEY", "")
CLOUDINARY_API_SECRET = os.getenv("CLOUDINARY_API_SECRET", "")

# Validate required environment variables
def validate_config():
    """Validate that all required environment variables are set"""
    # In mock mode, skip validation of API keys
    if MOCK_MODE:
        print("⚠️  MOCK MODE ENABLED - Skipping API key validation")
        return

    required_vars = {
        "FREEPIK_API_KEY": FREEPIK_API_KEY,
        "CLOUDINARY_CLOUD_NAME": CLOUDINARY_CLOUD_NAME,
        "CLOUDINARY_API_KEY": CLOUDINARY_API_KEY,
        "CLOUDINARY_API_SECRET": CLOUDINARY_API_SECRET,
    }

    missing_vars = [var for var, value in required_vars.items() if not value]

    if missing_vars:
        raise ValueError(
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please check your .env file"
        )

# Validate on import
validate_config()
