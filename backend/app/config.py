'''import os
from dotenv import load_dotenv

load_dotenv()'''

import os
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()

print("=" * 60)
print("DOTENV PATH:", dotenv_path)
print("=" * 60)

load_dotenv(dotenv_path)

print("RESEND_API_KEY:", os.getenv("RESEND_API_KEY"))
print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
print("=" * 60)

class Settings:
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

    RESEND_API_KEY: str = os.getenv("RESEND_API_KEY", "")
    RESEND_FROM_EMAIL: str = os.getenv("RESEND_FROM_EMAIL", "onboarding@resend.dev")
    SEND_REAL_EMAILS: bool = os.getenv("SEND_REAL_EMAILS", "true").lower() == "true"

    print("ENV SEND_REAL_EMAILS =", os.getenv("SEND_REAL_EMAILS"))
    print("ENV RESEND_API_KEY =", os.getenv("RESEND_API_KEY"))
    print("ENV TEST_RECIPIENT_EMAIL =", os.getenv("TEST_RECIPIENT_EMAIL"))

    # TESTING ONLY: Resend won't deliver to arbitrary addresses until you verify
    # a domain — it only delivers to the email you signed up to Resend with.
    # Set this to that address and every real send gets redirected here instead
    # of the (fake, Faker-generated) customer email, so you can actually see
    # mail land in an inbox. Remove/unset once you verify a domain in production.
    TEST_RECIPIENT_EMAIL: str = os.getenv("TEST_RECIPIENT_EMAIL", "")

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./revenue_recovery.db")

    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173"
    ).split(",")

    # --- Stopping rules / compliance defaults (the "bar" requirements) ---
    MAX_CONTACT_ATTEMPTS: int = 4
    COOLDOWN_HOURS_BETWEEN_ATTEMPTS: int = 24
    MAX_PURSUIT_DAYS: int = 21
    QUIET_HOURS_START: int = 21  # 9 PM
    QUIET_HOURS_END: int = 8     # 8 AM


settings = Settings()
