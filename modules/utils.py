import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_env_variable(key):
    """Fetches the value of an environment variable."""
    value = os.getenv(key)
    if not value:
        raise EnvironmentError(f"Environment variable {key} is missing.")
    return value
