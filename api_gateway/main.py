from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from api_gateway.handlers import router

app = FastAPI(title="API Gateway")


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(req: Request, exc: RequestValidationError):
    missing_params = []

    for error in exc.errors():
        # missing query params
        if error["loc"] and "query" in error["loc"] and error["type"] == "missing":
            missing_params.append(error["loc"][-1])

        # invalid UUID format
        if error["type"] == "uuid_parsing":
            field = error["loc"][-1]

            return JSONResponse(
                status_code=400,
                content={"message": f"Invalid UUID format for parameter: '{field}'"},
            )

    if missing_params:
        return JSONResponse(
            status_code=400,
            content={
                "message": f"Missing required parameter(s): {', '.join(missing_params)}"
            },
        )

    # fallback for other validation errors
    return JSONResponse(
        status_code=422, content={"message": "Invalid request", "details": exc.errors()}
    )


app.include_router(router)
