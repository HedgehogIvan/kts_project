from marshmallow import Schema, fields


class AnswerSchema(Schema):
    text = fields.Str(required=True)
    reward = fields.Int(required=True)


class QuestionSchema(Schema):
    title = fields.Str(required=True)
    answers = fields.Nested("AnswerSchema", many=True, required=True)
