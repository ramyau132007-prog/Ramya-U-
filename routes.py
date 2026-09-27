"""
routes.py
Core routing logic for FitBuddy — bridges the frontend templates, the
Gemini-powered AI generation modules, and the SQLite database.
"""

import os

from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.schemas import UserInput, WorkoutRequest, FeedbackRequest
from app.gemini_generator import generate_workout_gemini
from app.gemini_flash_generator import generate_nutrition_tip_with_flash
from app.updated_plan import update_workout_plan
from app.database import (
    save_user,
    save_plan,
    update_plan,
    get_original_plan,
    get_user,
    get_all_users,
    get_all_plans,
)

router = APIRouter()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)


# ---------------------------------------------------------------------------
# / – Home Route
# ---------------------------------------------------------------------------
@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    """Returns the homepage (index.html). No form processing logic."""
    return templates.TemplateResponse("index.html", {"request": request})


# ---------------------------------------------------------------------------
# /generate-workout – Plan Generator
# ---------------------------------------------------------------------------
@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout(
    request: Request,
    username: str = Form(...),
    user_id: int = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
):
    """
    Receives user input via Form(...), generates a workout plan + nutrition
    tip, saves everything, and renders result.html.
    """
    user_data = UserInput(
        username=username,
        user_id=user_id,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity,
    )

    # Generate plan via Gemini 1.5 Pro
    plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity})

    # Generate nutrition tip via Gemini Flash
    nutrition_tip = generate_nutrition_tip_with_flash(user_data.goal)

    # Persist
    save_user(
        user_id=user_data.user_id,
        name=user_data.username,
        age=user_data.age,
        weight=user_data.weight,
        goal=user_data.goal,
        intensity=user_data.intensity,
    )
    save_plan(user_data.user_id, plan, nutrition_tip)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user_data.username,
            "user_id": user_data.user_id,
            "age": user_data.age,
            "weight": user_data.weight,
            "goal": user_data.goal,
            "intensity": user_data.intensity,
            "workout_plan": plan,
            "nutrition_tip": nutrition_tip,
        },
    )


# ---------------------------------------------------------------------------
# /submit-feedback – Update Plan with Feedback
# ---------------------------------------------------------------------------
@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback(
    request: Request,
    user_id: int = Form(...),
    feedback: str = Form(...),
):
    """
    Captures feedback + user_id, retrieves the original plan, revises it via
    Gemini 1.5 Pro, stores the update, and re-renders result.html.
    """
    user = get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    original = get_original_plan(user_id)
    if not original:
        raise HTTPException(status_code=404, detail="Original plan not found for this user.")

    updated = update_workout_plan(original, feedback)
    update_plan(user_id, updated)

    nutrition_tip = generate_nutrition_tip_with_flash(user.goal)

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "username": user.name,
            "user_id": user.id,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "workout_plan": updated,
            "nutrition_tip": nutrition_tip,
            "feedback_submitted": True,
        },
    )


# ---------------------------------------------------------------------------
# /view-all-users – Admin View
# ---------------------------------------------------------------------------
@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(request: Request):
    """Displays all registered users and their original/updated plans."""
    users = get_all_users()
    plans = {p.user_id: p for p in get_all_plans()}

    user_data = []
    for user in users:
        plan = plans.get(user.id)
        user_data.append(
            {
                "id": user.id,
                "name": user.name,
                "age": user.age,
                "weight": user.weight,
                "goal": user.goal,
                "intensity": user.intensity,
                "original_plan": plan.original_plan if plan else "N/A",
                "updated_plan": plan.updated_plan if plan and plan.updated_plan else "Not updated",
            }
        )

    return templates.TemplateResponse(
        "all_users.html",
        {"request": request, "users": user_data},
    )


# ---------------------------------------------------------------------------
# JSON API endpoints (for /docs testing, mirrors the HTML routes above)
# ---------------------------------------------------------------------------
@router.post("/api/generate-workout")
def api_generate_workout(payload: WorkoutRequest):
    """API: Generate workout using Gemini Pro."""
    try:
        result = generate_workout_gemini({"goal": payload.goal, "intensity": payload.intensity})
        return {"model": "gemini-1.5-pro", "workout_plan": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/nutrition-tip")
def api_nutrition_tip(goal: str):
    """API: Generate nutrition tip using Gemini Flash."""
    tip = generate_nutrition_tip_with_flash(goal)
    return {"goal": goal, "nutrition_tip": tip}


@router.post("/api/generate-plan")
def api_generate_plan(user_data: UserInput):
    """API: Save user info & generate plan."""
    try:
        save_user(
            user_id=user_data.user_id,
            name=user_data.username,
            age=user_data.age,
            weight=user_data.weight,
            goal=user_data.goal,
            intensity=user_data.intensity,
        )
        plan = generate_workout_gemini({"goal": user_data.goal, "intensity": user_data.intensity})
        save_plan(user_data.user_id, plan)
        return {"message": "Workout plan generated and saved successfully!", "workout_plan": plan}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Something went wrong: {str(e)}")


@router.post("/api/update-plan/{user_id}", response_model=dict)
def api_update_plan(user_id: int, data: FeedbackRequest):
    """API: Update workout plan based on user feedback."""
    original = get_original_plan(user_id)
    if not original:
        return {"error": "Original plan not found for this user."}
    updated = update_workout_plan(original, data.feedback)
    update_plan(user_id, updated)
    return {"updated_plan": updated}
