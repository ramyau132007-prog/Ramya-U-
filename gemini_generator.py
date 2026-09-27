"""
gemini_generator.py
Gemini 1.5 Pro — structured 7-day workout plan generation and
feedback-based plan updates.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY:
    genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel("gemini-1.5-pro")


def generate_workout_gemini(user_input: dict) -> str:
    """
    Generate a personalized, structured 7-day workout plan.

    Args:
        user_input (dict): expects "goal" and "intensity" keys.

    Returns:
        str: the generated workout plan (or an error message).
    """
    prompt = f"""
    You are a professional fitness trainer.

    Create a personalized, structured 7-day workout plan for someone with the goal of
    **{user_input['goal']}**, and prefers **{user_input['intensity']} intensity** workouts.

    Each day must include:
    - A warm-up (5-10 mins)
    - Main workout (targeted exercises, sets & reps)
    - Cooldown or recovery tip

    Format:
    Day 1:
    Warm-up: ...
    Main Workout: ...
    Cooldown: ...
    (Repeat for Day 2-7)
    """
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"
