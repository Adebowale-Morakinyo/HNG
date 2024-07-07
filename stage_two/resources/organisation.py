from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..models import UserModel, OrganisationModel, UserOrganisation
from ..schemas import OrganisationSchema, AddUserToOrganisationSchema

import uuid

blp = Blueprint("Organisations", "organisations", description="Operations on organisations")


@blp.route("/api/organisations")
class OrganisationList(MethodView):
    @jwt_required()
    @blp.response(200, OrganisationSchema(many=True))
    def get(self):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user)
        if not user:
            abort(404, message="User not found.")
        organisations = OrganisationModel.query.filter_by(user_id=user.userId).all()
        return {
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {"organisations": organisations}
        }

    @jwt_required()
    @blp.arguments(OrganisationSchema)
    @blp.response(201, OrganisationSchema)
    def post(self, organisation_data):
        current_user = get_jwt_identity()
        user = UserModel.find_by_id(current_user)
        if not user:
            abort(404, message="User not found.")

        organisation = OrganisationModel(
            orgId=str(uuid.uuid4()),
            name=organisation_data["name"],
            description=organisation_data.get("description", "")
        )
        organisation.save_to_db()

        # Add current user to the organisation
        user_organisation = UserOrganisation(user_id=user.userId, org_id=organisation.orgId)
        user_organisation.save_to_db()

        return {
            "status": "success",
            "message": "Organisation created successfully",
            "data": organisation
        }


@blp.route("/api/organisations/<string:org_id>")
class Organisation(MethodView):
    @jwt_required()
    @blp.response(200, OrganisationSchema)
    def get(self, org_id):
        organisation = OrganisationModel.query.filter_by(orgId=org_id).first()
        if not organisation:
            abort(404, message="Organisation not found.")
        return {
            "status": "success",
            "message": "Organisation retrieved successfully",
            "data": organisation
        }

    @jwt_required()
    @blp.arguments(OrganisationSchema)
    @blp.response(200, OrganisationSchema)
    def put(self, organisation_data, org_id):
        organisation = OrganisationModel.query.filter_by(orgId=org_id).first()
        if not organisation:
            abort(404, message="Organisation not found.")

        organisation.name = organisation_data["name"]
        organisation.description = organisation_data["description"]
        organisation.save_to_db()

        return organisation

    @jwt_required()
    def delete(self, org_id):
        organisation = OrganisationModel.query.filter_by(orgId=org_id).first()
        if not organisation:
            abort(404, message="Organisation not found.")

        organisation.delete_from_db()
        return {"message": "Organisation deleted."}, 200


@blp.route("/api/organisations/<string:org_id>/users")
class AddUserToOrganisation(MethodView):
    @jwt_required()
    @blp.arguments(AddUserToOrganisationSchema)
    def post(self, user_data, org_id):
        organisation = OrganisationModel.query.filter_by(orgId=org_id).first()
        if not organisation:
            abort(404, message="Organisation not found.")

        user = UserModel.find_by_id(user_data["userId"])
        if not user:
            abort(404, message="User not found.")

        user_organisation = UserOrganisation(user_id=user.userId, org_id=organisation.orgId)
        user_organisation.save_to_db()

        return {"status": "success", "message": "User added to organisation successfully"}, 200
