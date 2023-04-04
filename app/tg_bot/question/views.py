from dataclasses import asdict

from aiohttp.web_exceptions import HTTPForbidden, HTTPConflict, HTTPException, HTTPBadRequest
from aiohttp.web_response import json_response
from aiohttp_apispec import request_schema

from .models import Answer, Question
from .schemes import QuestionSchema
from ...web.aiohttp_extansion import View
from ...web.utils import available_for_admin

__all__ = ["QuestionCreateView"]


class QuestionCreateView(View):
    @request_schema(QuestionSchema)
    @available_for_admin
    async def post(self):
        data = await self.request.json()

        title = data["title"]
        answers = data["answers"]

        if len(answers) < 5:
            raise HTTPBadRequest

        if await self.store.questions.get_question_by_title(title):
            raise HTTPConflict

        answers_list = [Answer(answer["text"], answer["reward"]) for answer in answers]
        question: Question = await self.store.questions.create_question(title, answers_list)

        return json_response(data={"status": "ok", "question": asdict(question)})
