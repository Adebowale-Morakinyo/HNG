from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity

from models import UserModel, OrganisationModel, UserOrganisation
from schemas import OrganisationSchema, AddUserToOrganisationSchema

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

        user_organisations = UserOrganisation.query.filter_by(user_id=user.userId).all()
        organisations = [uo.organisation for uo in user_organisations]

        return {
            "status": "success",
            "message": "Organisations retrieved successfully",
            "data": {"organisations": [org.json() for org in organisations]}
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

        user_organisation = UserOrganisation(user_id=user.userId, org_id=organisation.orgId)
        user_organisation.save_to_db()

        return {
            "status": "success",
            "message": "Organisation created successfully",
            "data": organisation.json()
        }, 201


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
        current_user = get_jwt_identity()
        current_user_model = UserModel.find_by_id(current_user)
        if not current_user_model:
            abort(404, message="Current user not found.")

        organisation = OrganisationModel.query.filter_by(orgId=org_id).first()
        if not organisation:
            abort(404, message="Organisation not found.")

        current_user_org = UserOrganisation.query.filter_by(user_id=current_user, org_id=org_id).first()
        if not current_user_org:
            abort(403, message="You don't have permission to add users to this organisation.")

        user_to_add = UserModel.find_by_id(user_data["userId"])
        if not user_to_add:
            abort(404, message="User to add not found.")

        existing_user_org = UserOrganisation.query.filter_by(user_id=user_to_add.userId, org_id=org_id).first()
        if existing_user_org:
            return {"status": "success", "message": "User is already in this organisation"}, 200

        user_organisation = UserOrganisation(user_id=user_to_add.userId, org_id=organisation.orgId)
        user_organisation.save_to_db()

        return {"status": "success", "message": "User added to organisation successfully"}, 200
