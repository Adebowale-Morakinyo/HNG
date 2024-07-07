from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    get_jwt_identity,
)
from passlib.hash import pbkdf2_sha256
import uuid

from ..models import UserModel, OrganisationModel
from ..schemas import UserSchema, UserRegisterSchema, UserLoginSchema
from ..blocklist import BLOCKLIST

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/auth/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        if UserModel.find_by_email(user_data["email"]):
            abort(400, message="A user with that email already exists.")

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

        return user


@blp.route("/auth/login")
class UserLogin(MethodView):
    @blp.arguments(UserLoginSchema)
    def post(self, user_data):
        user = UserModel.find_by_email(user_data["email"])
        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.userId)
            return {"accessToken": access_token}, 200

        abort(401, message="Invalid credentials.")


@blp.route("/api/users/string:user_id")
class User(MethodView):
    @jwt_required()
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.find_by_id(user_id)
        if not user:
            abort(404, message="User not found.")
        return user