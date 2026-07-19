"""
Ye file sirf HTTP endpoints define karti hai.
Har route ek service function ko call karta hai - koi business logic yahan nahi hoti.
"""

from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.integrations.linkedin import oauth, service
from app.integrations.linkedin.schemas import (
    LinkedInPostRequest,
    LinkedInConnectResponse,
    LinkedInProfileResponse,
    LinkedInPostResponse,
    LinkedInDisconnectResponse,
)
from app.integrations.linkedin.exceptions import (
    LinkedInAccountNotFoundError,
    LinkedInTokenExpiredError,
    LinkedInAPIError,
    LinkedInAuthError,
)

router = APIRouter(prefix="/api/linkedin", tags=["LinkedIn"])


# NOTE: abhi user_id query param se le rahe hain testing ke liye.
# Jab tumhara auth system (login) ready ho jaye, isse "current logged-in user"
# se replace kar dena (e.g. Depends(get_current_user))


@router.get("/connect", response_model=LinkedInConnectResponse)
def connect(user_id: int):
    login_url = oauth.get_login_url(user_id)
    return {"login_url": login_url}


from fastapi.responses import RedirectResponse
from app.core.config import settings

@router.get("/callback")
async def callback(code: str, state: str, db: Session = Depends(get_db)):
    user_id = int(state)
    try:
        account = await oauth.handle_callback(db, user_id, code)
        return RedirectResponse(url=f"{settings.FRONTEND_URL}?connected=true")
    except LinkedInAuthError as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/profile", response_model=LinkedInProfileResponse)
async def get_profile(user_id: int, db: Session = Depends(get_db)):
    try:
        return await service.get_profile(db, user_id)
    except LinkedInAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LinkedInTokenExpiredError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/post", response_model=LinkedInPostResponse)
async def create_post(
    payload: LinkedInPostRequest, user_id: int, db: Session = Depends(get_db)
):
    try:
        return await service.publish_to_linkedin(db, user_id, payload.text)
    except LinkedInAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LinkedInTokenExpiredError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LinkedInAPIError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))


@router.post("/post-image", response_model=LinkedInPostResponse)
async def create_image_post(
    user_id: int,
    text: str = Form(...),
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    try:
        image_bytes = await image.read()
        return await service.publish_to_linkedin(
            db, user_id, text, image_bytes=image_bytes
        )
    except LinkedInAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except LinkedInTokenExpiredError as e:
        raise HTTPException(status_code=401, detail=str(e))
    except LinkedInAPIError as e:
        raise HTTPException(status_code=e.status_code or 500, detail=str(e))


@router.delete("/disconnect", response_model=LinkedInDisconnectResponse)
async def disconnect(user_id: int, db: Session = Depends(get_db)):
    try:
        return await service.disconnect(db, user_id)
    except LinkedInAccountNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/analytics")
def get_analytics(user_id: int):
    return service.get_analytics(user_id)


@router.get("/articles")
def get_articles(user_id: int):
    return service.get_articles_status(user_id)
