import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_get_activities():
    """Test retrieving all activities."""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]
    assert "max_participants" in data["Chess Club"]

def test_signup_success():
    """Test successful signup for an activity."""
    email = "newstudent@mergington.edu"
    activity = "Chess Club"
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Signed up" in result["message"]
    
    # Verify the student was added
    response = client.get("/activities")
    data = response.json()
    assert email in data[activity]["participants"]

def test_signup_duplicate():
    """Test signing up for the same activity twice."""
    email = "dupstudent@mergington.edu"
    activity = "Programming Class"
    # First signup
    client.post(f"/activities/{activity}/signup?email={email}")
    # Second signup (should fail)
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "already signed up" in result["detail"]

def test_signup_activity_not_found():
    """Test signing up for a non-existent activity."""
    response = client.post("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_unregister_success():
    """Test successful unregistration from an activity."""
    email = "removestudent@mergington.edu"
    activity = "Gym Class"
    # First sign up
    client.post(f"/activities/{activity}/signup?email={email}")
    # Then unregister
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    result = response.json()
    assert "Unregistered" in result["message"]
    
    # Verify the student was removed
    response = client.get("/activities")
    data = response.json()
    assert email not in data[activity]["participants"]

def test_unregister_not_signed_up():
    """Test unregistering a student who isn't signed up."""
    email = "notsigned@mergington.edu"
    activity = "Art Club"
    response = client.delete(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    result = response.json()
    assert "not signed up" in result["detail"]

def test_unregister_activity_not_found():
    """Test unregistering from a non-existent activity."""
    response = client.delete("/activities/Nonexistent Activity/signup?email=test@mergington.edu")
    assert response.status_code == 404
    result = response.json()
    assert "Activity not found" in result["detail"]

def test_root_redirect():
    """Test root endpoint redirects to static page."""
    response = client.get("/")
    assert response.status_code == 200  # RedirectResponse, but TestClient follows redirects
    # In FastAPI TestClient, redirects are followed by default
    assert "text/html" in response.headers.get("content-type", "")