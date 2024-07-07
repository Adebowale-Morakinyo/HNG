from marshmallow import Schema, fields, validate


class AddUserToOrganisationSchema(Schema):
    userId = fields.String(required=True, validate=validate.Length(min=1))
