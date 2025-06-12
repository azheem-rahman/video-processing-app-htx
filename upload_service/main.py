from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from upload_service.handlers import router

app = FastAPI(title="Upload Service")


@app.exception_handler(RequestValidationError)
async def handle_request_validation_error(req: Request, exc: RequestValidationError):
    for error in exc.errors():
        # missing file in form-data
        if error["loc"] and "file" in error["loc"] and error["type"] == "missing":
            return JSONResponse(
                status_code=400,
                content={
                    "message": "You must include a video file in the request form-data."
                },
            )

        # invalid UUID format
        if error["type"] == "uuid_parsing":
            field = error["loc"][-1]

            return JSONResponse(
                status_code=400,
                content={"message": f"Invalid UUID format for parameter: '{field}'"},
            )

    # fallback for other validation errors
    return JSONResponse(
        status_code=422, content={"message": "Invalid request", "detail": exc.errors()}
    )


app.include_router(router)
