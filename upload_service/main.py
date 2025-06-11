from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from upload_service.handlers import router

app = FastAPI(title="Upload Service")


# return custom message if request does not have any files attached
@app.exception_handler(RequestValidationError)
async def handle_missing_file(req: Request, exc: RequestValidationError):
    for error in exc.errors():
        if error["loc"] and "file" in error["loc"] and error["type"] == "missing":
            return JSONResponse(
                status_code=400,
                content={
                    "message": "You must include a video file in the request form-data."
                },
            )

    # fallback for other validation errors
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


app.include_router(router)
