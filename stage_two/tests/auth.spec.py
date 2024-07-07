import unittest
from flask_jwt_extended import create_access_token, decode_token
from datetime import timedelta

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

    def test_user_registration_success(self):
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
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Registration successful")

        # Check if default organisation was created
        user = UserModel.find_by_email("john.doe@example.com")
        org = OrganisationModel.query.filter_by(name="John's Organisation").first()
        self.assertIsNotNone(org)
        self.assertIn(user.userId, [uo.user_id for uo in org.users])

    def test_user_registration_missing_fields(self):
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com"
        }
        response = self.client.post("/auth/register", json=user_data)
        self.assertEqual(response.status_code, 422)
        self.assertIn("errors", response.json)

    def test_user_registration_duplicate_email(self):
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "phone": "1234567890"
        }
        self.client.post("/auth/register", json=user_data)
        response = self.client.post("/auth/register", json=user_data)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["status"], "Bad request")
        self.assertEqual(response.json["message"], "Registration unsuccessful")

    def test_user_login_success(self):
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "phone": "1234567890"
        }
        self.client.post("/auth/register", json=user_data)
        login_data = {
            "email": "john.doe@example.com",
            "password": "password"
        }
        response = self.client.post("/auth/login", json=login_data)
        self.assertEqual(response.status_code, 200)
        self.assertIn("accessToken", response.json["data"])
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Login successful")

    def test_user_login_invalid_credentials(self):
        login_data = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        response = self.client.post("/auth/login", json=login_data)
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json["status"], "Bad request")
        self.assertEqual(response.json["message"], "Authentication failed")

    def test_create_organisation_success(self):
        # First, register a user
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "phone": "1234567890"
        }
        register_response = self.client.post("/auth/register", json=user_data)
        access_token = register_response.json["data"]["accessToken"]

        # Now create an organisation
        org_data = {
            "name": "Test Organisation",
            "description": "This is a test organisation."
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        response = self.client.post("/api/organisations", json=org_data, headers=headers)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Organisation created successfully")
        self.assertIn("orgId", response.json["data"])
        self.assertEqual(response.json["data"]["name"], "Test Organisation")

    def test_get_organisations(self):
        # First, register a user and create an organisation
        user_data = {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john.doe@example.com",
            "password": "password",
            "phone": "1234567890"
        }
        register_response = self.client.post("/auth/register", json=user_data)
        access_token = register_response.json["data"]["accessToken"]

        org_data = {
            "name": "Test Organisation",
            "description": "This is a test organisation."
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        self.client.post("/api/organisations", json=org_data, headers=headers)

        # Now get the organisations
        response = self.client.get("/api/organisations", headers=headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["status"], "success")
        self.assertEqual(response.json["message"], "Organisations retrieved successfully")
        self.assertGreaterEqual(len(response.json["data"]["organisations"]), 1)  # Should have at least the default org

    def test_token_expiration(self):
        with self.app.app_context():
            user = UserModel(
                userId="test_user_id",
                firstName="John",
                lastName="Doe",
                email="john.doe@example.com",
                password="password",
                phone="1234567890"
            )
            user.save_to_db()

            # Create a token that expires in 1 second
            access_token = create_access_token(identity=user.userId, expires_delta=timedelta(seconds=1))

            # Wait for 2 seconds
            import time
            time.sleep(2)

            # Try to decode the token
            with self.assertRaises(Exception):  # This should raise an ExpiredSignatureError
                decode_token(access_token)

if __name__ == "__main__":
    unittest.main()