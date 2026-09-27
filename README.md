# FitBuddy – AI Fitness Plan Generator (Gemini Models)

FastAPI + Gemini-powered app that generates personalized 7-day workout
plans and nutrition tips, and lets users refine plans with feedback.

## Setup

```bash
python -m venv fitbuddy-env
source fitbuddy-env/bin/activate      # Windows: fitbuddy-env\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and add your key:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

## Run

```bash
uvicorn app.main:app --reload
```

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Pages / Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Home page — input form |
| `/generate-workout` | POST | Generate plan + nutrition tip, save, show result |
| `/submit-feedback` | POST | Revise plan based on feedback |
| `/view-all-users` | GET | Admin dashboard of all users & plans |
| `/api/generate-workout` | POST | JSON API — generate workout only |
| `/api/nutrition-tip` | GET | JSON API — nutrition tip only |
| `/api/generate-plan` | POST | JSON API — save user + generate plan |
| `/api/update-plan/{user_id}` | POST | JSON API — update plan via feedback |

## Structure

```
fitbuddy/
├── requirements.txt
├── .env.example
└── app/
    ├── main.py                    # FastAPI entry point
    ├── routes.py                  # Route handlers
    ├── database.py                # SQLAlchemy models + DB helpers
    ├── schemas.py                 # Pydantic request models
    ├── gemini_generator.py        # Gemini 1.5 Pro — workout generation
    ├── gemini_flash_generator.py  # Gemini Flash — nutrition tips
    ├── updated_plan.py            # Gemini 1.5 Pro — feedback-based updates
    ├── templates/
    │   ├── index.html
    │   ├── result.html
    │   └── all_users.html
    └── static/images/
```

Data (users + plans) persists in `fitbuddy.db` (SQLite), created
automatically on first run.
