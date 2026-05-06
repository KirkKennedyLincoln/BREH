from pydantic import BaseModel, Field


class Step(BaseModel):
    id: str
    tool: str
    args: dict
    weight: float = Field(ge=0.0, le=1.0)
    depends_on: list[str] = []


class Graph(BaseModel):
    id: str
    request: str
    created_at: int
    steps: list[Step]
