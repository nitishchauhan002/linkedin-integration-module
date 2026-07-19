from pydantic import BaseModel
from typing import Optional


class LinkedInPostRequest(BaseModel):
    text: str
    image_url: Optional[str] = None


class LinkedInProfileResponse(BaseModel):
    linkedin_id: str
    name: str
    email: Optional[str] = None
    profile_picture: Optional[str] = None


class LinkedInConnectResponse(BaseModel):
    login_url: str


class LinkedInPostResponse(BaseModel):
    success: bool
    post_id: Optional[str] = None
    message: str


class LinkedInDisconnectResponse(BaseModel):
    success: bool
    message: str
