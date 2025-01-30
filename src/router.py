from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def health():
    return 200


@router.post("/api/request", response_model=PredictionResponse)
async def predict(body: PredictionRequest):
    try:
        await logger.info(f"Processing prediction request with id: {body.id}")
        # Здесь будет вызов вашей модели
        answer = 1  # Замените на реальный вызов модели
        sources: List[HttpUrl] = [
            HttpUrl("https://itmo.ru/ru/"),
            HttpUrl("https://abit.itmo.ru/"),
        ]

        response = PredictionResponse(
            id=body.id,
            answer=answer,
            reasoning="Из информации на сайте",
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
