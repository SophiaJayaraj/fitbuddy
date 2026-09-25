import os
from pathlib import Path


# -----------------------------------------
# TEST CONFIGURATION
# -----------------------------------------

TEST_DB = (
    Path(__file__)
    .resolve()
    .parent.parent
    / "test_fitbuddy.db"
)


if TEST_DB.exists():

    TEST_DB.unlink()


# Use demo mode so tests don't call Gemini
os.environ["DEMO_MODE"] = "true"

os.environ["DATABASE_URL"] = (
    f"sqlite:///{TEST_DB.as_posix()}"
)


# -----------------------------------------
# IMPORT APPLICATION
# -----------------------------------------

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


# -----------------------------------------
# HEALTH TEST
# -----------------------------------------

def test_health():

    response = client.get(
        "/health"
    )

    assert response.status_code == 200

    assert (
        "running"
        in response.json()["message"]
    )


# -----------------------------------------
# HOME PAGE TEST
# -----------------------------------------

def test_home():

    response = client.get("/")

    assert response.status_code == 200

    assert "FitBuddy" in response.text


# -----------------------------------------
# GENERATE + FEEDBACK TEST
# -----------------------------------------

def test_generate_and_feedback():

    payload = {

        "name":
            "Test User",

        "user_id":
            "TEST001",

        "age":
            20,

        "weight_kg":
            65,

        "goal":
            "general wellness",

        "intensity":
            "medium",
    }


    response = client.post(
        "/api/workouts/generate",
        json=payload
    )


    assert (
        response.status_code == 200
    )


    body = response.json()


    assert (
        body["user_id"]
        == "TEST001"
    )


    assert body["workout_plan"]


    # Feedback

    feedback_response = client.post(

        "/api/workouts/feedback",

        json={
            "user_id":
                "TEST001",

            "feedback":
                "Please add more recovery."
        }
    )


    assert (
        feedback_response.status_code
        == 200
    )


    assert (
        feedback_response.json()
        ["updated_plan"]
    )


# -----------------------------------------
# USER LIST TEST
# -----------------------------------------

def test_users():

    response = client.get(
        "/api/users"
    )


    assert response.status_code == 200


    users = response.json()


    assert any(
        user["user_id"]
        == "TEST001"
        for user in users
    )


# -----------------------------------------
# DELETE TEST
# -----------------------------------------

def test_delete_user():

    response = client.delete(
        "/api/users/TEST001"
    )


    assert (
        response.status_code
        == 200
    )


    response = client.get(
        "/api/users/TEST001"
    )


    assert (
        response.status_code
        == 404
    )