from marshmallow import Schema, fields


class AdminScheme(Schema):
    id = fields.Int(required=False)
    login = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True)


class AdminChangePasswordSchema(Schema):
    old_pass = fields.Str(required=True)
    new_pass = fields.Str(required=True)


class AdminDeleteSchema(Schema):
    admin_for_delete = fields.Str(required=True)
    password = fields.Str(required=True)
