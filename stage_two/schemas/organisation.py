from marshmallow import Schema, fields, validate


class OrganisationSchema(Schema):
    orgId = fields.Str(required=True)
    name = fields.Str(required=True)
    description = fields.Str()


class OrganisationResponseSchema(Schema):
    status = fields.Str(required=True)
    message = fields.Str(required=True)
    data = fields.Nested(OrganisationSchema)


class OrganisationListResponseSchema(Schema):
    status = fields.Str(required=True)
    message = fields.Str(required=True)
    data = fields.Nested(Schema.from_dict({
        "organisations": fields.List(fields.Nested(OrganisationSchema))
    }))


class CreateOrganisationSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1))
    description = fields.Str()


class CreateOrganisationResponseSchema(Schema):
    status = fields.Str(required=True)
    message = fields.Str(required=True)
    data = fields.Nested(OrganisationSchema)
