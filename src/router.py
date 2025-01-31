import json

from fastapi import APIRouter, HTTPException
from pydantic.networks import HttpUrl
from typing import List

from logger import logger
from agent import graph
from schemas.request import PredictionRequest, PredictionResponse

router = APIRouter()


@router.get("/")
def health():
    return {"status": "ok"}


@router.post("/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await logger.info(f"Processing prediction request with id: {body.id}")
        # //
        config = {"configurable": {"thread_id": "1"}}
        events = graph.stream(
            {
                "messages": [
                    {
                        "role": "user",
                        "content": body.query,
                    },
                ],
            },
            config,
            stream_mode="values",
        )
        answer = []
        for event in events:
            if "messages" in event:
                answer += event["messages"][-1]

        answer = " ".join(answer)
        logger.info(answer)

        sources: List[HttpUrl] = [
            HttpUrl("https://itmo.ru/ru/"),
            HttpUrl("https://abit.itmo.ru/"),
        ]

        response = PredictionResponse(
            id=body.id,
            answer=1,
            reasoning=answer,
            sources=sources,
        )
        await logger.info(f"Successfully processed request {body.id}")
        return response
    except ValueError as e:
        error_msg = str(e)
        await logger.error(f"Validation error for request {body.id}: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)
    except Exception as e:
        await logger.error(f"Internal error processing request {body.id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


# events = graph.stream(
#     {
#         "messages": [
#             {
#                 "role": "user",
#                 "content": (
#                     "I'm learning LangGraph. Could you do some research on it for me?"
#                 ),
#             },
#         ],
#     },
#     config,
#     stream_mode="values",
# )
# for event in events:
#     if "messages" in event:
#         event["messages"][-1].pretty_print()
