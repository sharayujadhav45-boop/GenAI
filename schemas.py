"""Pydantic models that guarantee a clean quiz structure."""
from pydantic import BaseModel, Field, field_validator, model_validator


class MCQ(BaseModel):
    question: str = Field(min_length=1)
    options: list[str] = Field(min_length=2)
    answer_index: int = Field(strict=True, ge=0)
    explanation: str = Field(min_length=1)

    @field_validator("question", "explanation")
    @classmethod
    def non_empty_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be empty")
        return value

    @field_validator("options")
    @classmethod
    def valid_options(cls, options: list[str]) -> list[str]:
        cleaned = [option.strip() for option in options]
        if any(not option for option in cleaned):
            raise ValueError("options must not be empty")
        if len({option.casefold() for option in cleaned}) != len(cleaned):
            raise ValueError("options must be unique")
        return cleaned

    @model_validator(mode="after")
    def check(self):
        if not 0 <= self.answer_index < len(self.options):
            raise ValueError("answer_index out of range")
        return self


class Quiz(BaseModel):
    questions: list[MCQ] = Field(min_length=1)

    @model_validator(mode="after")
    def unique_questions(self):
        questions = [question.question.casefold() for question in self.questions]
        if len(set(questions)) != len(questions):
            raise ValueError("questions must be unique")
        return self
