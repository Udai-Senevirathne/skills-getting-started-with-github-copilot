"""
Tests for the Mergington High School Activities API
"""
import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivities:
    """Tests for activities endpoints"""

    def test_get_activities(self):
        """Test retrieving all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        
        # Check activity structure
        chess_club = activities["Chess Club"]
        assert "description" in chess_club
        assert "schedule" in chess_club
        assert "max_participants" in chess_club
        assert "participants" in chess_club
        assert isinstance(chess_club["participants"], list)

    def test_get_activities_has_initial_participants(self):
        """Test that activities have initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        # Chess Club should have initial participants
        assert len(activities["Chess Club"]["participants"]) > 0
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_for_activity_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Drama Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        assert "Drama Club" in result["message"]

    def test_signup_for_activity_duplicate_email(self):
        """Test signup fails when student already registered"""
        # First signup
        client.post("/activities/Tennis Club/signup?email=duplicate@mergington.edu")
        
        # Second signup with same email
        response = client.post(
            "/activities/Tennis Club/signup?email=duplicate@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "detail" in result
        assert "already signed up" in result["detail"]

    def test_signup_for_nonexistent_activity(self):
        """Test signup fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_unregister_from_activity_success(self):
        """Test successful unregister from an activity"""
        # First, sign up
        client.post("/activities/Gym Class/signup?email=unregister_test@mergington.edu")
        
        # Then unregister
        response = client.post(
            "/activities/Gym Class/unregister?email=unregister_test@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "Unregistered" in result["message"]

    def test_unregister_from_activity_not_registered(self):
        """Test unregister fails when student not registered"""
        response = client.post(
            "/activities/Basketball Team/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "detail" in result
        assert "not registered" in result["detail"]

    def test_unregister_from_nonexistent_activity(self):
        """Test unregister fails for non-existent activity"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result
        assert "not found" in result["detail"]

    def test_signup_and_unregister_workflow(self):
        """Test the complete signup and unregister workflow"""
        email = "workflow_test@mergington.edu"
        activity = "Debate Team"
        
        # Get initial state
        response = client.get("/activities")
        activities_before = response.json()
        initial_count = len(activities_before[activity]["participants"])
        
        # Sign up
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        assert signup_response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        activities_after_signup = response.json()
        assert len(activities_after_signup[activity]["participants"]) == initial_count + 1
        assert email in activities_after_signup[activity]["participants"]
        
        # Unregister
        unregister_response = client.post(
            f"/activities/{activity}/unregister?email={email}"
        )
        assert unregister_response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        activities_after_unregister = response.json()
        assert len(activities_after_unregister[activity]["participants"]) == initial_count
        assert email not in activities_after_unregister[activity]["participants"]

    def test_static_files_redirect(self):
        """Test that root redirects to static files"""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200
