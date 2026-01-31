import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# Email configuration
MAIL_FROM = os.getenv("MAIL_FROM")
MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
MAIL_PORT = int(os.getenv("MAIL_PORT", 587))  # Convert to int with a default value
MAIL_SERVER = os.getenv("MAIL_SERVER")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME")

# Parse boolean values correctly
MAIL_TLS = os.getenv("MAIL_TLS", "False").lower() == "true"
MAIL_SSL = os.getenv("MAIL_SSL", "False").lower() == "true"
USE_CREDENTIALS = os.getenv("USE_CREDENTIALS", "False").lower() == "true"
VALIDATE_CERTS = os.getenv("VALIDATE_CERTS", "False").lower() == "true"

SECRET_APP_KEY = os.getenv("SECRET_APP_KEY")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 10 * 24 * 60))

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")
FRONT_END_URI = os.getenv("FRONT_END_URI")

DISTANCEMATRIX_ACCURATE_KEY = os.getenv("DISTANCEMATRIX_ACCURATE_KEY")

UPLOAD_DIR = os.getenv("UPLOAD_DIR")

IMPACTCO2_API_KEY = os.getenv("IMPACTCO2_API_KEY")

# Validate critical configurations
if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set in the .env file")
