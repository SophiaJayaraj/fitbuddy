from .ai_service import generate_text
from .config import settings
from .schemas import UserInput


def update_workout_plan(
    original_plan: str,
    feedback: str,
    user: UserInput
) -> str:

    if settings.demo_mode:

        return (
            original_plan
            + "\n\n"
            + "UPDATED USING USER FEEDBACK\n"
            + "--------------------------------\n"
            + f"Feedback: {feedback}\n\n"
            + "The demo version keeps the original plan "
              "and demonstrates the feedback workflow.\n"
            + "The requested change should be applied "
              "gradually while keeping recovery time."
        )

    prompt = f"""
Revise the FitBuddy 7-day wellness plan based on
the user's feedback.

USER

Name:
{user.name}

Age:
{user.age}

Goal:
{user.goal.value}

Intensity:
{user.intensity.value}


USER FEEDBACK

{feedback}


ORIGINAL PLAN

{original_plan}


Return a COMPLETE revised Day 1–Day 7 plan.

Do not return only a diff.

Apply reasonable user feedback.

Keep useful parts of the original plan.

Include recovery/rest.

Include a short safety note.

Do not provide:

- Calorie restriction
- Extreme dieting
- Supplements
- Dangerous challenges
- Medical treatment

Do not use appearance-based pressure.
"""

    return generate_text(
        prompt,
        settings.workout_model
    )