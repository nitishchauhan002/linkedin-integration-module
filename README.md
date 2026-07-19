# LinkedIn Integration Module

## Setup

1. Virtual environment banao aur activate karo:
   ```
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # Mac/Linux
   ```

2. Dependencies install karo:
   ```
   pip install -r requirements.txt
   ```

3. `.env.example` ko `.env` mein rename karo aur apni LinkedIn Client ID/Secret daalo:
   ```
   cp .env.example .env
   ```

4. Server run karo:
   ```
   uvicorn app.main:app --reload
   ```

5. Browser mein kholo: http://localhost:8000/docs
   (Swagger UI se sab endpoints test kar sakte ho)

## Flow test karne ka tarika

1. `GET /api/linkedin/connect` call karo → `login_url` milega
2. Us URL ko browser mein kholo, LinkedIn se login/allow karo
3. LinkedIn tumhe `redirect_uri` pe `?code=...` ke saath bhejega
4. Wahi `code` le kar `GET /api/linkedin/callback?code=XXX&user_id=1` call karo
5. Account connect ho jayega, ab `/api/linkedin/profile?user_id=1` aur
   `/api/linkedin/post?user_id=1` (body me `{"text": "Hello LinkedIn"}`) try karo

## Folder Structure

```
app/
├── core/
│   └── config.py          # env variables
├── integrations/
│   └── linkedin/
│       ├── router.py      # API endpoints
│       ├── service.py     # business logic (baaki team members isse call karenge)
│       ├── oauth.py       # OAuth flow
│       ├── client.py      # raw LinkedIn API calls
│       ├── schemas.py     # request/response models
│       ├── models.py      # database table
│       ├── exceptions.py  # custom errors
│       └── utils.py       # helper functions
├── database.py
└── main.py
```

## Scheduler / team ke liye public functions

Team ke baaki members ko sirf ye functions use karne hain
(`app/integrations/linkedin/service.py` se import karke):

```python
from app.integrations.linkedin.service import (
    publish_to_linkedin,
    get_profile,
    disconnect,
)

await publish_to_linkedin(db, user_id, text="Hello", image_bytes=None)
```

Inke andar LinkedIn API, tokens, OAuth - kuch bhi pata karne ki zarurat nahi.

## Known Limitations (Free Developer Tier)

| Feature | Status |
|---|---|
| OAuth Login | ✅ Working |
| Profile Fetch | ✅ Working |
| Text Post | ✅ Working |
| Image Post | ✅ Working |
| Analytics | ⚠️ Not available (needs partner access) - graceful fallback returned |
| Articles | ⚠️ Not available (needs partner access) - graceful fallback returned |
