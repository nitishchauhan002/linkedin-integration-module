from sqlalchemy import Column, Integer, String, DateTime
from app.database import Base

class LinkedInAccount(Base):
    __tablename__ = "linkedin_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    linkedin_id = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=True)
    email = Column(String, nullable=True)
    profile_picture = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False)
