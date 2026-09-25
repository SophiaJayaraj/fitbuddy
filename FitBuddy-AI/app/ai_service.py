from functools import lru_cache

from google import genai

from .config import settings


class AIServiceError(RuntimeError):
    """
    Raised when Gemini cannot generate a usable response.
    """
    pass


SYSTEM_GUARDRAILS = """
You are the AI engine for FitBuddy, a general wellness application.

Safety requirements:

- Provide general wellness and fitness education.
- Do not provide medical diagnosis or treatment.
- Do not prescribe medication.
- Do not recommend dangerous exercise challenges.
- Do not provide extreme fasting or restrictive dieting instructions.
- Do not provide calorie restriction targets.
- Do not use body shaming or appearance-based pressure.
- Encourage gradual progression, rest, hydration, sleep,
  and balanced meals.
- If the user is under 18, keep guidance conservative and
  encourage involvement of a parent, guardian, coach,
  or qualified health professional.
"""


@lru_cache(maxsize=1)
def get_client():

    if not settings.google_api_key:

        raise AIServiceError(
            "GOOGLE_API_KEY is not configured. "
            "Add it to .env or enable DEMO_MODE=true."
        )

    return genai.Client(
        api_key=settings.google_api_key
    )


def generate_text(
    prompt: str,
    model: str
) -> str:

    if settings.demo_mode:

        return ""

    try:

        response = get_client().models.generate_content(
            model=model,
            contents=(
                SYSTEM_GUARDRAILS
                + "\n\n"
                + prompt
            ),
        )

    except Exception as exc:

        raise AIServiceError(
            f"Gemini request failed: {exc}"
        ) from exc

    text = getattr(
        response,
        "text",
        None
    )

    if not text or not text.strip():

        raise AIServiceError(
            "Gemini returned an empty response."
        )

    return text.strip()