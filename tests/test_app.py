import pytest
from fastapi.testclient import TestClient

from src import app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Test activity",
            "schedule": "Mondays",
            "max_participants": 12,
            "participants": ["existing@example.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_signup_adds_student_to_activity(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Signed up new@example.edu for Chess Club"}
    assert "new@example.edu" in app_module.activities["Chess Club"]["participants"]


def test_signup_rejects_duplicate_student(client):
    response = client.post(
        "/activities/Chess%20Club/signup",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Student is already signed up for this activity"
    }


def test_signup_rejects_unknown_activity(client):
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "new@example.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_student_and_any_duplicate_entries(client):
    app_module.activities["Chess Club"]["participants"].append("existing@example.edu")

    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "message": "Unregistered existing@example.edu from Chess Club"
    }
    assert "existing@example.edu" not in app_module.activities["Chess Club"]["participants"]


def test_unregister_rejects_student_not_signed_up(client):
    response = client.delete(
        "/activities/Chess%20Club/participants",
        params={"email": "missing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Student is not signed up for this activity"
    }


def test_unregister_rejects_unknown_activity(client):
    response = client.delete(
        "/activities/Unknown/participants",
        params={"email": "existing@example.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
