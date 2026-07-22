from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.integrations.linkedin.router import router as linkedin_router
from app.integrations.linkedin import models  # noqa: F401 - table registration ke liye zaroori

app = FastAPI(title="Social Media Tool - Backend")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)

app.include_router(linkedin_router)

@app.get("/")
def root():
    return {"message": "Backend running", "docs": "/docs"}
