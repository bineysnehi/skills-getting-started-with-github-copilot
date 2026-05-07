import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

BASE_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(BASE_ACTIVITIES))
    yield


def test_get_activities_returns_all():
    # Arrange
    expected_activity = BASE_ACTIVITIES["Chess Club"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    payload = response.json()
    assert "Chess Club" in payload
    assert payload["Chess Club"]["description"] == expected_activity["description"]
    assert payload["Chess Club"]["participants"] == expected_activity["participants"]


def test_signup_adds_participant():
    # Arrange
    activity_name = quote("Chess Club")
    email = "new.student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert "Signed up" in response.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    # Arrange
    activity_name = quote("Chess Club")
    email = BASE_ACTIVITIES["Chess Club"]["participants"][0]

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up for this activity"


def test_unregister_removes_participant():
    # Arrange
    activity_name = quote("Chess Club")
    email = BASE_ACTIVITIES["Chess Club"]["participants"][0]

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={quote(email)}")

    # Assert
    assert response.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_non_registered_returns_400():
    # Arrange
    activity_name = quote("Chess Club")
    email = "unknown.student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={quote(email)}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not registered for this activity"


def test_invalid_activity_returns_404_for_signup():
    # Arrange
    activity_name = quote("Nonexistent Club")
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={quote(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_invalid_activity_returns_404_for_unregister():
    # Arrange
    activity_name = quote("Nonexistent Club")
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister?email={quote(email)}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
