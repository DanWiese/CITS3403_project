import os
import tempfile
import unittest

# Create temporary database for tests before importing app
db_fd, db_path = tempfile.mkstemp()
os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"

from app import app, db, User


class AppUnitTests(unittest.TestCase):

    def setUp(self):
        app.config["TESTING"] = True
        app.config["SECRET_KEY"] = "test-secret-key"

        self.client = app.test_client()

        with app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def signup_user(self):
        return self.client.post("/signup", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        })

    def test_signup_creates_user(self):
        response = self.signup_user()

        self.assertEqual(response.status_code, 201)

        with app.app_context():
            user = User.query.filter_by(email="test@example.com").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.username, "testuser")
            self.assertNotEqual(user.password, "password123")

    def test_signup_rejects_duplicate_email(self):
        self.signup_user()

        response = self.client.post("/signup", json={
            "username": "anotheruser",
            "email": "test@example.com",
            "password": "password123"
        })

        self.assertEqual(response.status_code, 409)

    def test_login_rejects_wrong_password(self):
        self.signup_user()

        response = self.client.post("/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })

        self.assertEqual(response.status_code, 401)

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard", follow_redirects=False)

        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.location)

    def test_create_event_requires_login(self):
        response = self.client.post("/events", json={
            "title": "Test Event",
            "start_date": "2026-05-20",
            "start_time": "14:00"
        })

        self.assertEqual(response.status_code, 302)

    def test_create_event_rejects_missing_title(self):
        self.signup_user()

        response = self.client.post("/events", json={
            "title": "",
            "location": "UWA",
            "description": "Missing title test",
            "start_date": "2026-05-20",
            "start_time": "14:00",
            "end_date": "2026-05-20",
            "end_time": "16:00"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("Event name is required", response.get_json()["message"])

    def test_create_event_rejects_end_before_start(self):
        self.signup_user()

        response = self.client.post("/events", json={
            "title": "Bad Time Event",
            "location": "UWA",
            "description": "Invalid time test",
            "start_date": "2026-05-20",
            "start_time": "16:00",
            "end_date": "2026-05-20",
            "end_time": "14:00"
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("End date and time must be after", response.get_json()["message"])


if __name__ == "__main__":
    unittest.main()