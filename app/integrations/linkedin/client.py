"""
Ye file sirf LinkedIn ke raw HTTP endpoints ko call karti hai.
Isme koi business logic nahi hoti - sirf request/response.
"""

import httpx
from urllib.parse import urlencode
from app.core.config import settings
from app.integrations.linkedin.exceptions import LinkedInAPIError, LinkedInAuthError

AUTH_URL = "https://www.linkedin.com/oauth/v2/authorization"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
USERINFO_URL = "https://api.linkedin.com/v2/userinfo"
POST_URL = "https://api.linkedin.com/v2/ugcPosts"
ASSET_REGISTER_URL = "https://api.linkedin.com/v2/assets?action=registerUpload"


def build_authorization_url(state: str = None) -> str:
    params = {
        "response_type": "code",
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "scope": "openid profile email w_member_social",
    }
    if state:
        params["state"] = state

    return f"{AUTH_URL}?{urlencode(params)}"


async def fetch_access_token(code: str) -> dict:
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": settings.LINKEDIN_REDIRECT_URI,
        "client_id": settings.LINKEDIN_CLIENT_ID,
        "client_secret": settings.LINKEDIN_CLIENT_SECRET,
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(TOKEN_URL, data=data)

    if response.status_code != 200:
        raise LinkedInAuthError(f"Token exchange failed: {response.text}")

    return response.json()


async def fetch_profile(access_token: str) -> dict:
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.get(USERINFO_URL, headers=headers)

    if response.status_code != 200:
        raise LinkedInAPIError(
            f"Profile fetch failed: {response.text}",
            status_code=response.status_code,
        )

    return response.json()


async def create_text_post(access_token: str, person_urn: str, text: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(POST_URL, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        raise LinkedInAPIError(
            f"Post publish failed: {response.text}",
            status_code=response.status_code,
        )

    return {"post_id": response.headers.get("x-restli-id", "unknown")}


async def register_image_upload(access_token: str, person_urn: str) -> dict:
    """Image post karne se pehle LinkedIn ko batana padta hai ki upload hone wala hai"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": person_urn,
            "serviceRelationships": [
                {
                    "relationshipType": "OWNER",
                    "identifier": "urn:li:userGeneratedContent",
                }
            ],
        }
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(
            ASSET_REGISTER_URL, headers=headers, json=payload
        )

    if response.status_code != 200:
        raise LinkedInAPIError(
            f"Image register failed: {response.text}",
            status_code=response.status_code,
        )

    return response.json()


async def upload_image_binary(upload_url: str, access_token: str, image_bytes: bytes):
    headers = {"Authorization": f"Bearer {access_token}"}
    async with httpx.AsyncClient() as client:
        response = await client.put(upload_url, headers=headers, content=image_bytes)

    if response.status_code not in (200, 201):
        raise LinkedInAPIError(
            f"Image upload failed: {response.text}",
            status_code=response.status_code,
        )


async def create_image_post(
    access_token: str, person_urn: str, text: str, asset_urn: str
) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": person_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE",
                "media": [
                    {
                        "status": "READY",
                        "media": asset_urn,
                    }
                ],
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(POST_URL, headers=headers, json=payload)

    if response.status_code not in (200, 201):
        raise LinkedInAPIError(
            f"Image post publish failed: {response.text}",
            status_code=response.status_code,
        )

    return {"post_id": response.headers.get("x-restli-id", "unknown")}
