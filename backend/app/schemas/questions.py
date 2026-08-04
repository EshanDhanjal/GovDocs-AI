from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
        description="Question about U.S. immigration or government documents.",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of knowledge-base passages to retrieve.",
    )