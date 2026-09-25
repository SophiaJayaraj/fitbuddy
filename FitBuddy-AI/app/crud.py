from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from .models import User, WorkoutPlan
from .schemas import UserInput


def get_user(
    db: Session,
    user_id: str
):

    return db.scalar(
        select(User)
        .where(
            User.user_id == user_id
        )
        .options(
            selectinload(User.plans)
        )
    )


def save_user(
    db: Session,
    data: UserInput
):

    user = db.scalar(
        select(User)
        .where(
            User.user_id == data.user_id
        )
    )

    if user is None:

        user = User(
            user_id=data.user_id,
            name=data.name,
            age=data.age,
            weight_kg=data.weight_kg,
            goal=data.goal.value,
            intensity=data.intensity.value,
        )

        db.add(user)

    else:

        user.name = data.name
        user.age = data.age
        user.weight_kg = data.weight_kg
        user.goal = data.goal.value
        user.intensity = data.intensity.value

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    original_plan: str,
    nutrition_tip: str
):

    plan = WorkoutPlan(
        user_id=user.id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip,
    )

    db.add(plan)

    db.commit()
    db.refresh(plan)

    return plan


def get_latest_plan(
    db: Session,
    user: User
):

    return db.scalar(
        select(WorkoutPlan)
        .where(
            WorkoutPlan.user_id == user.id
        )
        .order_by(
            WorkoutPlan.created_at.desc()
        )
    )


def update_plan(
    db: Session,
    plan: WorkoutPlan,
    updated_plan: str,
    feedback: str
):

    plan.updated_plan = updated_plan
    plan.feedback = feedback
    plan.updated_at = datetime.utcnow()

    db.commit()
    db.refresh(plan)

    return plan


def get_all_users(
    db: Session
):

    return list(
        db.scalars(
            select(User)
            .options(
                selectinload(User.plans)
            )
            .order_by(
                User.created_at.desc()
            )
        ).all()
    )