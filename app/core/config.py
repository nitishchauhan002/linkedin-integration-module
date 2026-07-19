import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    LINKEDIN_CLIENT_ID = os.getenv("LINKEDIN_CLIENT_ID")
    LINKEDIN_CLIENT_SECRET = os.getenv("LINKEDIN_CLIENT_SECRET")
    LINKEDIN_REDIRECT_URI = os.getenv("LINKEDIN_REDIRECT_URI")
    FRONTEND_URL = os.getenv("FRONTEND_URL")   # ← ye line add karo


settings = Settings()