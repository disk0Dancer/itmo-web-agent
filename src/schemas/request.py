from typing import List
from pydantic import Field

from pydantic import BaseModel, HttpUrl


class PredictionRequest(BaseModel):
    id: int
    query: str


class PredictionResponse(BaseModel):
    id: int
    answer: int = None
    reasoning: str
    sources: List[HttpUrl]


class AgentOutput(BaseModel):
    answer_option: int = Field(
        None,
        description="integer if you are asked to select correct option from list, or -1 if no options",
    )
    reasoning: str = Field("", description="explain why did you choose selected answer")
    sources: List[HttpUrl] = Field(
        description="list of sources used to generate answer if there any",
    )
