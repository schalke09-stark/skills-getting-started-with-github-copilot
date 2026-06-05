"""
Tests for the Mergington High School Activities API
Uses the AAA (Arrange-Act-Assert) testing pattern
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Verify endpoint returns 200 status code"""
        # Arrange
        # No setup needed for this test

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Verify endpoint returns a dictionary of activities"""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_get_activities_contains_required_fields(self):
        """Verify each activity has required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        assert len(data) > 0
        for activity_name, activity_data in data.items():
            for field in required_fields:
                assert field in activity_data, f"Missing field '{field}' in activity '{activity_name}'"
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_has_expected_activities(self):
        """Verify the activities list contains expected activities"""
        # Arrange
        expected_activities = ["Chess Club", "Programming Class", "Gym Class"]

        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        for activity in expected_activities:
            assert activity in data


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self):
        """Verify successful signup returns 200"""
        # Arrange
        email = "success-test@mergington.edu"
        activity_name = "Science%20Club"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self):
        """Verify signup actually adds participant to activity"""
        # Arrange
        email = "participant-test@mergington.edu"
        activity_name = "Debate%20Team"

        # Get initial participant count
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()["Debate Team"]["participants"])

        # Act
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert - verify signup was successful
        assert signup_response.status_code == 200

        # Assert - verify participant count increased
        final_response = client.get("/activities")
        final_count = len(final_response.json()["Debate Team"]["participants"])
        assert final_count == initial_count + 1

        # Assert - verify specific participant is in list
        assert email in final_response.json()["Debate Team"]["participants"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Verify signup returns 404 for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity_name = "NonExistent%20Activity"

        # Act
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_email_returns_400(self):
        """Verify signup returns 400 when student already signed up"""
        # Arrange
        email = "duplicate-test@mergington.edu"
        activity_name = "Art%20Studio"

        # First signup should succeed
        first_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert first_response.status_code == 200

        # Act
        duplicate_response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert
        assert duplicate_response.status_code == 400
        assert "already signed up" in duplicate_response.json()["detail"]

    def test_signup_full_activity_returns_400(self):
        """Verify signup returns 400 when activity is at max capacity"""
        # Arrange
        activity_name = "Basketball%20Team"
        max_capacity = 15

        # Fill the activity to capacity
        for i in range(max_capacity):
            email = f"capacity-test{i}@mergington.edu"
            response = client.post(f"/activities/{activity_name}/signup?email={email}")
            assert response.status_code == 200

        # Act - try to add one more participant
        overflow_email = "overflow-test@mergington.edu"
        overflow_response = client.post(
            f"/activities/{activity_name}/signup?email={overflow_email}"
        )

        # Assert
        assert overflow_response.status_code == 400
        assert "full" in overflow_response.json()["detail"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants endpoint"""

    def test_remove_participant_successful(self):
        """Verify successful participant removal returns 200"""
        # Arrange
        email = "remove-test@mergington.edu"
        activity_name = "Science%20Club"

        # Sign up the participant first
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_participant_removes_from_list(self):
        """Verify participant is actually removed from activity"""
        # Arrange
        email = "verify-remove@mergington.edu"
        activity_name = "Drama%20Club"

        # Sign up the participant
        client.post(f"/activities/{activity_name}/signup?email={email}")

        # Verify participant is in the list
        pre_remove_response = client.get("/activities")
        assert email in pre_remove_response.json()["Drama Club"]["participants"]

        # Act
        client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        post_remove_response = client.get("/activities")
        assert email not in post_remove_response.json()["Drama Club"]["participants"]

    def test_remove_nonexistent_participant_returns_404(self):
        """Verify remove returns 404 for participant not in activity"""
        # Arrange
        email = "nonexistent@mergington.edu"
        activity_name = "Chess%20Club"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Participant not found" in response.json()["detail"]

    def test_remove_from_nonexistent_activity_returns_404(self):
        """Verify remove returns 404 for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        activity_name = "FakeActivity"

        # Act
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static_index(self):
        """Verify root endpoint redirects to /static/index.html"""
        # Arrange
        # No setup needed

        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestIntegrationScenarios:
    """Integration tests for real-world workflows"""

    def test_complete_signup_and_view_workflow(self):
        """Test full workflow: get activities → signup → verify in list"""
        # Arrange
        email = "integration-test@mergington.edu"
        activity_name = "Swimming%20Club"

        # Act 1 - Get activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert "Swimming Club" in activities

        # Act 2 - Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200

        # Assert - Verify participant appears in updated list
        updated_response = client.get("/activities")
        updated_activities = updated_response.json()
        assert email in updated_activities["Swimming Club"]["participants"]

    def test_signup_remove_and_verify_workflow(self):
        """Test workflow: signup → remove → verify removal"""
        # Arrange
        email = "workflow-test@mergington.edu"
        activity_name = "Debate%20Team"

        # Act 1 - Sign up
        signup_response = client.post(f"/activities/{activity_name}/signup?email={email}")
        assert signup_response.status_code == 200

        # Assert 1 - Verify participant is added
        check_response = client.get("/activities")
        assert email in check_response.json()["Debate Team"]["participants"]

        # Act 2 - Remove participant
        remove_response = client.delete(f"/activities/{activity_name}/participants?email={email}")
        assert remove_response.status_code == 200

        # Assert 2 - Verify participant is removed
        final_response = client.get("/activities")
        assert email not in final_response.json()["Debate Team"]["participants"]
