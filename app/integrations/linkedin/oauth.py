"""
Ye file OAuth flow ko manage karti hai:
login URL banana, code ko token me convert karna, DB me save karna.
"""

from sqlalchemy.orm import Session
from app.integrations.linkedin import client, utils
from app.integrations.linkedin.models import LinkedInAccount


def get_login_url(user_id: int) -> str:
    return client.build_authorization_url(state=str(user_id))


async def handle_callback(db: Session, user_id: int, code: str) -> LinkedInAccount:
    """
    Authorization code aane ke baad:
    1. Access token lo
    2. Profile fetch karo
    3. DB me save/update karo
    """
    token_data = await client.fetch_access_token(code)
    access_token = token_data["access_token"]
    expires_in = token_data.get("expires_in", 3600)

    profile = await client.fetch_profile(access_token)

    existing_account = (
        db.query(LinkedInAccount)
        .filter(LinkedInAccount.user_id == user_id)
        .first()
    )

    expires_at = utils.calculate_token_expiry(expires_in)

    if existing_account:
        existing_account.linkedin_id = profile["sub"]
        existing_account.name = profile.get("name")
        existing_account.email = profile.get("email")
        existing_account.profile_picture = profile.get("picture")
        existing_account.access_token = access_token
        existing_account.expires_at = expires_at
        db.commit()
        db.refresh(existing_account)
        return existing_account

    new_account = LinkedInAccount(
        user_id=user_id,
        linkedin_id=profile["sub"],
        name=profile.get("name"),
        email=profile.get("email"),
        profile_picture=profile.get("picture"),
        access_token=access_token,
        expires_at=expires_at,
    )
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
