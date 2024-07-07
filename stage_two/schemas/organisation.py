from marshmallow import Schema, fields


class OrganisationSchema(Schema):
    orgId = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
