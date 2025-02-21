from fastapi import APIRouter, HTTPException

from src.logger import logger
from src.agent import graph, formatting, reasoning_summary, get_sources, model
from src.schemas.request import PredictionRequest, PredictionResponse

router = APIRouter()


@router.get("/")
def health():
    return {"status": "ok"}


@router.post("/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await logger.info(f"Processing prediction request with id: {body.id}")

        response = await graph.ainvoke(
            input={
                "messages": [
                    {
                        "role": "system",
                        "content": "ITMO абитуриенту нужна информация!",
                    },
                    {
                        "role": "user",
                        "content": body.query,
                    },
                ]
            },
            config={"configurable": {"thread_id": "1"}},
            stream_mode="values",
        )

        answer = (await formatting(response["messages"])).content
        reasoning = (
            f"response generated by: {model}\n"
            + (await reasoning_summary(response["messages"])).content
        )
        sources = (await get_sources(response["messages"])).content.split(",")

        logger.info(answer)
        logger.info(reasoning)
        logger.info(sources)

        response = PredictionResponse(
            id=body.id,
            answer=answer,
            reasoning=reasoning,
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
