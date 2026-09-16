import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "roughset_challenge_secret_key_2024_secure_amenallah")
    
    # Firebase Firestore Configuration
    FIREBASE_CREDENTIALS_PATH = os.environ.get("FIREBASE_CREDENTIALS_PATH", "firebase-key.json")
    FIREBASE_CREDENTIALS_JSON = os.environ.get("FIREBASE_CREDENTIALS_JSON", "")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "")
    
    # Admin Credentials
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "Amenallah")
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "Amen1920")
    ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", "")
    
    # Application settings
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_PERMANENT = False
    PORT = int(os.environ.get("PORT", 5005))
    DEBUG = os.environ.get("FLASK_ENV") == "development" or os.environ.get("DEBUG", "true").lower() == "true"
