from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from .ai_service import AIServiceError
from .crud import (
    get_all_users,
    get_latest_plan,
    get_user,
    save_plan,
    save_user,
    update_plan,
)

from .database import get_db

from .gemini_flash_generator import (
    generate_nutrition_tip_with_flash,
)

from .gemini_generator import (
    generate_workout_gemini,
)

from .schemas import (
    FeedbackRequest,
    MessageResponse,
    PlanResponse,
    UserInput,
)

from .updated_plan import (
    update_workout_plan,
)


BASE_DIR = Path(__file__).resolve().parent.parent

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)

router = APIRouter()


def render_error(
    request: Request,
    message: str,
    status_code: int = 400
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": message
        },
        status_code=status_code,
    )


def build_plan_response(
    user,
    plan
):

    return PlanResponse(
        user_id=user.user_id,
        name=user.name,
        goal=user.goal,
        intensity=user.intensity,
        workout_plan=plan.original_plan,
        nutrition_tip=plan.nutrition_tip,
        updated_plan=plan.updated_plan,
    )


# --------------------------------------------------
# HOME
# --------------------------------------------------

@router.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "error": None
        },
    )


# --------------------------------------------------
# GENERATE WORKOUT - HTML
# --------------------------------------------------

@router.post(
    "/generate-workout",
    response_class=HTMLResponse
)
def generate_workout(
    request: Request,

    name: str = Form(...),

    user_id: str = Form(...),

    age: int = Form(...),

    weight_kg: float = Form(...),

    goal: str = Form(...),

    intensity: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = UserInput(
            name=name,
            user_id=user_id,
            age=age,
            weight_kg=weight_kg,
            goal=goal,
            intensity=intensity,
        )

        # Gemini workout
        workout_plan = (
            generate_workout_gemini(data)
        )

        # Gemini nutrition tip
        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data
            )
        )

        # Save user
        user = save_user(
            db,
            data
        )

        # Save plan
        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": plan,
                "message": (
                    "Your 7-day plan has been generated."
                ),
            },
        )

    except (
        ValueError,
        AIServiceError
    ) as exc:

        return render_error(
            request,
            str(exc)
        )

    except Exception as exc:

        return render_error(
            request,
            f"Unexpected error: {exc}",
            500,
        )


# --------------------------------------------------
# SUBMIT FEEDBACK - HTML
# --------------------------------------------------

@router.post(
    "/submit-feedback",
    response_class=HTMLResponse
)
def submit_feedback(
    request: Request,

    user_id: str = Form(...),

    feedback: str = Form(...),

    db: Session = Depends(get_db),
):

    try:

        data = FeedbackRequest(
            user_id=user_id,
            feedback=feedback,
        )

        user = get_user(
            db,
            data.user_id
        )

        if user is None:

            return render_error(
                request,
                "User ID was not found.",
                404,
            )

        latest_plan = get_latest_plan(
            db,
            user
        )

        if latest_plan is None:

            return render_error(
                request,
                "No workout plan exists for this user.",
                404,
            )

        user_input = UserInput(
            name=user.name,
            user_id=user.user_id,
            age=user.age,
            weight_kg=user.weight_kg,
            goal=user.goal,
            intensity=user.intensity,
        )

        source_plan = (
            latest_plan.updated_plan
            or latest_plan.original_plan
        )

        revised_plan = (
            update_workout_plan(
                source_plan,
                data.feedback,
                user_input,
            )
        )

        update_plan(
            db,
            latest_plan,
            revised_plan,
            data.feedback,
        )

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "user": user,
                "plan": latest_plan,
                "message": (
                    "Your plan was updated using your feedback."
                ),
            },
        )

    except (
        ValueError,
        AIServiceError
    ) as exc:

        return render_error(
            request,
            str(exc)
        )

    except Exception as exc:

        return render_error(
            request,
            f"Unexpected error: {exc}",
            500,
        )


# --------------------------------------------------
# ADMIN VIEW
# --------------------------------------------------

@router.get(
    "/view-all-users",
    response_class=HTMLResponse
)
def view_all_users(
    request: Request,
    db: Session = Depends(get_db),
):

    users = get_all_users(db)

    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={
            "users": users
        },
    )


# --------------------------------------------------
# HEALTH CHECK
# --------------------------------------------------

@router.get(
    "/health",
    response_model=MessageResponse
)
def health():

    return {
        "message":
            "FitBuddy API is running."
    }


# --------------------------------------------------
# API - GENERATE
# --------------------------------------------------

@router.post(
    "/api/workouts/generate",
    response_model=PlanResponse
)
def api_generate_workout(
    data: UserInput,
    db: Session = Depends(get_db),
):

    try:

        workout_plan = (
            generate_workout_gemini(data)
        )

        nutrition_tip = (
            generate_nutrition_tip_with_flash(
                data
            )
        )

        user = save_user(
            db,
            data
        )

        plan = save_plan(
            db,
            user,
            workout_plan,
            nutrition_tip,
        )

        return build_plan_response(
            user,
            plan
        )

    except AIServiceError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc


# --------------------------------------------------
# API - FEEDBACK
# --------------------------------------------------

@router.post(
    "/api/workouts/feedback",
    response_model=PlanResponse
)
def api_feedback(
    data: FeedbackRequest,
    db: Session = Depends(get_db),
):

    user = get_user(
        db,
        data.user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User ID was not found."
        )

    latest_plan = get_latest_plan(
        db,
        user
    )

    if latest_plan is None:

        raise HTTPException(
            status_code=404,
            detail="No workout plan exists."
        )

    user_input = UserInput(
        name=user.name,
        user_id=user.user_id,
        age=user.age,
        weight_kg=user.weight_kg,
        goal=user.goal,
        intensity=user.intensity,
    )

    source_plan = (
        latest_plan.updated_plan
        or latest_plan.original_plan
    )

    try:

        revised_plan = (
            update_workout_plan(
                source_plan,
                data.feedback,
                user_input,
            )
        )

        update_plan(
            db,
            latest_plan,
            revised_plan,
            data.feedback,
        )

        return build_plan_response(
            user,
            latest_plan
        )

    except AIServiceError as exc:

        raise HTTPException(
            status_code=503,
            detail=str(exc)
        ) from exc


# --------------------------------------------------
# API - ALL USERS
# --------------------------------------------------

@router.get(
    "/api/users"
)
def api_users(
    db: Session = Depends(get_db)
):

    users = get_all_users(db)

    return [
        {
            "user_id": user.user_id,
            "name": user.name,
            "age": user.age,
            "weight_kg": user.weight_kg,
            "goal": user.goal,
            "intensity": user.intensity,
            "latest_plan_id":
                user.plans[0].id
                if user.plans
                else None,
        }
        for user in users
    ]


# --------------------------------------------------
# API - SINGLE USER
# --------------------------------------------------

@router.get(
    "/api/users/{user_id}"
)
def api_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    user = get_user(
        db,
        user_id
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User ID was not found."
        )

    plan = get_latest_plan(
        db,
        user
    )

    return {
        "user_id": user.user_id,
        "name": user.name,
        "age": user.age,
        "weight_kg": user.weight_kg,
        "goal": user.goal,
        "intensity": user.intensity,

        "plan":
            {
                "id": plan.id,
                "original_plan":
                    plan.original_plan,
                "updated_plan":
                    plan.updated_plan,
                "nutrition_tip":
                    plan.nutrition_tip,
                "feedback":
                    plan.feedback,
            }
            if plan
            else None,
    }


# --------------------------------------------------
# API - DELETE USER
# --------------------------------------------------

@router.delete(
    "/api/users/{user_id}",
    response_model=MessageResponse
)
def delete_user(
    user_id: str,
    db: Session = Depends(get_db)
):

    from .models import User

    user = (
        db.query(User)
        .filter(
            User.user_id == user_id
        )
        .first()
    )

    if user is None:

        raise HTTPException(
            status_code=404,
            detail="User ID was not found."
        )

    db.delete(user)
    db.commit()

    return {
        "message":
            f"User {user_id} and associated plans were deleted."
    }