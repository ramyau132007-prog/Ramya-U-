"""
database.py
SQLAlchemy models + persistence helpers for FitBuddy.

Stores:
- User table: id, name, age, weight, goal, intensity, schedule
- WorkoutPlan table: user_id, original_plan, updated_plan
"""

from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String, nullable=False)
    intensity = Column(String, nullable=False)
    schedule = Column(Integer, default=7)  # days in the plan


class WorkoutPlan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    original_plan = Column(String, nullable=True)
    updated_plan = Column(String, nullable=True)
    nutrition_tip = Column(String, nullable=True)


def init_db():
    """Create tables if they don't already exist."""
    Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------------------------
# User & Plan Storage helpers
# ---------------------------------------------------------------------------
def save_user(user_id: int, name: str, age: int, weight: float, goal: str, intensity: str):
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id=user_id).first()
        if existing:
            # Update existing user info
            existing.name = name
            existing.age = age
            existing.weight = weight
            existing.goal = goal
            existing.intensity = intensity
        else:
            # Create a new user
            user = User(
                id=user_id,
                name=name,
                age=age,
                weight=weight,
                goal=goal,
                intensity=intensity,
                schedule=7,  # default schedule
            )
            db.add(user)
        db.commit()
    finally:
        db.close()


def save_plan(user_id: int, plan: str, nutrition_tip: str = None):
    """Stores the (original) plan for a user."""
    db = SessionLocal()
    try:
        existing = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if existing:
            existing.original_plan = plan
            if nutrition_tip is not None:
                existing.nutrition_tip = nutrition_tip
        else:
            workout = WorkoutPlan(
                user_id=user_id,
                original_plan=plan,
                nutrition_tip=nutrition_tip,
            )
            db.add(workout)
        db.commit()
    finally:
        db.close()


def update_plan(user_id: int, updated_text: str):
    """Update the plan based on feedback."""
    db = SessionLocal()
    try:
        workout = db.query(WorkoutPlan).filter_by(user_id=user_id).first()
        if workout:
            workout.updated_plan = updated_text
            db.commit()
    finally:
        db.close()


def get_original_plan(user_id: int):
    db = SessionLocal()
    try:
        plan = db.query(WorkoutPlan).filter(WorkoutPlan.user_id == user_id).first()
        return plan.original_plan if plan else None
    finally:
        db.close()


def get_user(user_id: int):
    db = SessionLocal()
    try:
        return db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()


def get_all_users():
    db = SessionLocal()
    try:
        return db.query(User).all()
    finally:
        db.close()


def get_all_plans():
    db = SessionLocal()
    try:
        return db.query(WorkoutPlan).all()
    finally:
        db.close()
