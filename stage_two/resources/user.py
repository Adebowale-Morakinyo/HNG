from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from passlib.hash import pbkdf2_sha256
import uuid
from marshmallow import ValidationError

from models import UserModel, OrganisationModel, UserOrganisation
from schemas import UserSchema, UserRegisterSchema, UserLoginSchema, RegistrationResponseSchema, LoginResponseSchema

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, RegistrationResponseSchema)
    def post(self, user_data):
        try:
            if UserModel.find_by_email(user_data["email"]):
                return {"status": "Bad request", "message": "Registration unsuccessful", "statusCode": 400}, 400

            user = UserModel(
                userId=str(uuid.uuid4()),
                firstName=user_data["firstName"],
                lastName=user_data["lastName"],
                email=user_data["email"],
                password=pbkdf2_sha256.hash(user_data["password"]),
                phone=user_data["phone"],
            )
            user.save_to_db()

            # Create default organisation
            organisation = OrganisationModel(
                orgId=str(uuid.uuid4()),
                name=f"{user_data['firstName']}'s Organisation",
                description=""
            )
            organisation.save_to_db()

            # Add user to organisation
            user_organisation = UserOrganisation(user_id=user.userId, org_id=organisation.orgId)
            user_organisation.save_to_db()

            access_token = create_access_token(identity=user.userId)
            return {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.firstName,
                        "lastName": user.lastName,
                        "email": user.email,
                        "phone": user.phone,
                    },
                },
            }, 201

        except ValidationError as err:
            return {"status": "Bad request", "message": "Registration unsuccessful", "statusCode": 400}, 400


@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    @blp.response(200, LoginResponseSchema)
    def post(self, user_data):
        try:
            user = UserModel.find_by_email(user_data["email"])
            if user and pbkdf2_sha256.verify(user_data["password"], user.password):
                access_token = create_access_token(identity=user.userId)
                return {
                    "status": "success",
                    "message": "Login successful",
                    "data": {
                        "accessToken": access_token,
                        "user": {
                            "userId": user.userId,
                            "firstName": user.firstName,
                            "lastName": user.lastName,
                            "email": user.email,
                            "phone": user.phone,
                        },
                    },
                }, 200

            return {"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, 401

        except ValidationError as err:
            return {"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, 401


@blp.route("/api/users/<string:user_id>")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")

        # Check if the current user has access to this user's information
        if current_user != user_id:
            user_orgs = UserOrganisation.query.filter_by(user_id=current_user).all()
            user_org_ids = [uo.org_id for uo in user_orgs]
            if not UserOrganisation.query.filter_by(user_id=user_id, org_id__in=user_org_ids).first():
                abort(403, message="You don't have permission to access this user's information.")

        return {
            "status": "success",
            "message": "User retrieved successfully",
            "data": {
                "userId": user.userId,
                "firstName": user.firstName,
                "lastName": user.lastName,
                "email": user.email,
                "phone": user.phone
            }
        }
