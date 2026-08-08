from pydantic import BaseModel, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=1000,
        description="Question about an uploaded document.",
    )

    document_id: str | None = Field(
        default=None,
        description="Optional uploaded document ID.",
    )

    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Number of official knowledge-base passages to retrieve.",
    )