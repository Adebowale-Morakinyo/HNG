from marshmallow import Schema, fields, validate


class AddUserToOrganisationSchema(Schema):
    userId = fields.Str(required=True)


class AddUserToOrganisationResponseSchema(Schema):
    status = fields.Str(required=True)
    message = fields.Str(required=True)
