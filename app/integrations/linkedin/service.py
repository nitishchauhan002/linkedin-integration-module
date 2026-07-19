"""
Ye file LinkedIn module ka "public interface" hai.
Team ke baaki members (Scheduler, Frontend) sirf yahan ke functions call karenge:

    - get_profile(db, user_id)
    - publish_to_linkedin(db, user_id, text, image_bytes=None)
    - disconnect(db, user_id)

Unhe LinkedIn API, OAuth, tokens - kuch bhi andar se pata nahi chalega.
"""

from sqlalchemy.orm import Session
from app.integrations.linkedin import client, utils
from app.integrations.linkedin.models import LinkedInAccount
from app.integrations.linkedin.exceptions import (
    LinkedInAccountNotFoundError,
    LinkedInTokenExpiredError,
)


def _get_account_or_raise(db: Session, user_id: int) -> LinkedInAccount:
    account = (
        db.query(LinkedInAccount)
        .filter(LinkedInAccount.user_id == user_id)
        .first()
    )
    if not account:
        raise LinkedInAccountNotFoundError(
            f"User {user_id} ka LinkedIn account connected nahi hai"
        )
    if utils.is_token_expired(account.expires_at):
        raise LinkedInTokenExpiredError(
            "LinkedIn access token expire ho chuka hai. Reconnect required."
        )
    return account


async def get_profile(db: Session, user_id: int) -> dict:
    account = _get_account_or_raise(db, user_id)
    return {
        "linkedin_id": account.linkedin_id,
        "name": account.name,
        "email": account.email,
        "profile_picture": account.profile_picture,
    }


async def publish_to_linkedin(
    db: Session, user_id: int, text: str, image_bytes: bytes = None
) -> dict:
    """
    Scheduler (Member 5) sirf isi function ko call karega:

        publish_to_linkedin(db, user_id, text, media=None)

    Andar text post ya image post - automatically decide ho jayega.
    """
    account = _get_account_or_raise(db, user_id)
    person_urn = utils.build_person_urn(account.linkedin_id)

    if image_bytes:
        register_data = await client.register_image_upload(
            account.access_token, person_urn
        )
        upload_url = register_data["value"]["uploadMechanism"][
            "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
        ]["uploadUrl"]
        asset_urn = register_data["value"]["asset"]

        await client.upload_image_binary(
            upload_url, account.access_token, image_bytes
        )
        result = await client.create_image_post(
            account.access_token, person_urn, text, asset_urn
        )
    else:
        result = await client.create_text_post(
            account.access_token, person_urn, text
        )

    return {
        "success": True,
        "post_id": result.get("post_id"),
        "message": "Post published successfully",
    }


async def disconnect(db: Session, user_id: int) -> dict:
    account = _get_account_or_raise(db, user_id)
    db.delete(account)
    db.commit()
    return {"success": True, "message": "LinkedIn account disconnected"}


def get_analytics(user_id: int) -> dict:
    """
    LinkedIn free/basic API tier me analytics (likes, comments, shares)
    generally available nahi hota - partnership access chahiye hota hai.
    Isliye graceful fallback return kar rahe hain.
    """
    return {
        "supported": False,
        "reason": "LinkedIn analytics API requires special partner access - not available on standard developer tier",
    }


def get_articles_status(user_id: int) -> dict:
    """
    LinkedIn Articles API bhi standard developer app ko nahi milta.
    Fallback response.
    """
    return {
        "supported": False,
        "reason": "LinkedIn Articles publishing API is not available on standard developer access",
    }
