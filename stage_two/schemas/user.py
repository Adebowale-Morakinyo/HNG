from marshmallow import Schema, fields, validate


class UserSchema(Schema):
    userId = fields.Str(dump_only=True)
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    phone = fields.Str()


class UserRegisterSchema(Schema):
    firstName = fields.Str(required=True)
    lastName = fields.Str(required=True)
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)
    phone = fields.Str()


class UserLoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(load_only=True, required=True)