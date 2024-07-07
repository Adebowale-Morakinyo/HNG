import unittest
from flask_jwt_extended import create_access_token

from app import create_app
from db import db
from models import UserModel, OrganisationModel, UserOrganisation


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_registration(self):
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "phone": "1234567890"
        }
        response = self.client.post("/auth/register", json=user_data)
        self.assertEqual(response.status_code, 201)
        self.assertIn("accessToken", response.json["data"])

    def test_user_login(self):
        user = UserModel(
            userId="unique_id",
            firstName="John",
            lastName="Doe",
            email="john.doe@example.com",
            password="password",
            phone="1234567890"
        )
        user.save_to_db()
        login_data = {
            "email": "john.doe@example.com",
            "password": "password"
        }
        response = self.client.post("/auth/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("accessToken", response.json["data"])

    def test_create_organisation(self):
        user = UserModel(
            userId="unique_id",
            firstName="John",
            lastName="Doe",
            email="john.doe@example.com",
            password="password",
            phone="1234567890"
        )
        user.save_to_db()
        access_token = create_access_token(identity=user.userId)
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        org_data = {
            "name": "Test Organisation",
            "description": "This is a test organisation."
        }
        response = self.client.post("/api/organisations", json=org_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertIn("organisation", response.json["data"])


if __name__ == "__main__":
    unittest.main()
