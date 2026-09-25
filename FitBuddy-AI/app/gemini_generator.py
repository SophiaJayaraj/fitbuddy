from .ai_service import generate_text
from .config import settings
from .schemas import UserInput


def _demo_plan(user: UserInput) -> str:

    return f"""
FITBUDDY 7-DAY WELLNESS PLAN

Profile
--------------------
Name: {user.name}
Goal: {user.goal.value}
Intensity: {user.intensity.value}


DAY 1 — FULL BODY
--------------------
Warm-up:
5–10 minutes of easy movement.

Main Workout:
• Bodyweight squats
• Wall or incline push-ups
• Glute bridges
• Comfortable walking

Cooldown:
Gentle stretching and slow breathing.


DAY 2 — CARDIO & MOBILITY
--------------------
Warm-up:
5–10 minutes.

Main Workout:
• Comfortable walking or cycling
• Gentle mobility exercises

Cooldown:
Light stretching.


DAY 3 — STRENGTH BASICS
--------------------
Warm-up:
5–10 minutes.

Main Workout:
• Squats or sit-to-stand
• Supported rows if available
• Glute bridges
• Core stability

Cooldown:
Easy walking and mobility.


DAY 4 — RECOVERY
--------------------
Focus on:
• Light walking
• Gentle mobility
• Hydration
• Sleep
• Normal daily movement


DAY 5 — FULL BODY
--------------------
Warm-up:
5–10 minutes.

Main Workout:
Repeat comfortable strength movements from
earlier days without pushing through pain.

Cooldown:
Gentle mobility.


DAY 6 — CARDIO / FUN MOVEMENT
--------------------
Choose a safe activity you enjoy.

Keep the effort comfortable and controlled.

Finish with gentle mobility.


DAY 7 — REST & REFLECTION
--------------------
Take a rest day or gentle walk.

Reflect on:
• What felt comfortable?
• What did you enjoy?
• What would you like to improve?


PROGRESSION
--------------------
Increase difficulty gradually.
Do not push through pain or discomfort.


SAFETY NOTE
--------------------
This is general wellness information, not medical advice.

Stop if you experience pain, dizziness, faintness,
or feel unwell.

For individualized guidance, consult an appropriate
qualified professional or trusted adult.
"""


def generate_workout_gemini(
    user: UserInput
) -> str:

    if settings.demo_mode:

        return _demo_plan(user)

    prompt = f"""
Create a personalized 7-day general wellness workout plan.

User information:

Name:
{user.name}

Age:
{user.age}

Weight:
{user.weight_kg} kg

Fitness Goal:
{user.goal.value}

Preferred Intensity:
{user.intensity.value}


Create:

1. Profile summary

2. Day 1 through Day 7

3. Each day should contain:
   - Focus
   - Warm-up
   - Main activity
   - Exercises
   - Sets/repetitions or duration
   - Rest/recovery
   - Cooldown when appropriate

4. Include at least one recovery/rest day.

5. Include a progression section.

6. Include a short safety note.

Do not provide calorie restriction.

Do not recommend dangerous exercises.

Do not recommend supplements.

Do not make medical claims.

Do not focus success on appearance.

Use clear Markdown formatting.
"""

    return generate_text(
        prompt,
        settings.workout_model
    )