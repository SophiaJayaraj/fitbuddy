from .ai_service import generate_text
from .config import settings
from .schemas import UserInput


def _demo_tip(
    user: UserInput
) -> str:

    return (
        f"For {user.goal.value}, focus on regular balanced meals, "
        "hydration, adequate sleep, and recovery. "
        "Choose a variety of everyday foods rather than relying "
        "on supplements. For individualized nutrition advice, "
        "consult a qualified professional."
    )


def generate_nutrition_tip_with_flash(
    user: UserInput
) -> str:

    if settings.demo_mode:

        return _demo_tip(user)

    prompt = f"""
Give one concise nutrition or recovery tip.

User goal:
{user.goal.value}

Intensity:
{user.intensity.value}

Age:
{user.age}

Write 3–5 sentences.

Focus on:

- Balanced meals
- Hydration
- Sleep
- Recovery
- Everyday healthy food choices

Do not provide:

- Calorie targets
- Extreme dieting
- Restrictive eating
- Supplements
- Medical treatment

Do not use appearance-based claims.
"""

    return generate_text(
        prompt,
        settings.fast_model
    )