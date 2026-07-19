from datetime import datetime, timedelta


def calculate_token_expiry(expires_in: int) -> datetime:
    """LinkedIn 'expires_in' seconds deta hai, ise actual datetime mein convert karna"""
    return datetime.utcnow() + timedelta(seconds=expires_in)


def is_token_expired(expires_at: datetime) -> bool:
    return datetime.utcnow() >= expires_at


def build_person_urn(linkedin_id: str) -> str:
    """LinkedIn API posts ke liye is format ki zarurat padti hai"""
    return f"urn:li:person:{linkedin_id}"
