from fastapi import APIRouter, Request, Response
import httpx
import os

router = APIRouter()

UPLOAD_SERVICE_URL = os.getenv("UPLOAD_SERVICE_URL", "http://upload_service:8000")
QUERY_SERVICE_URL = os.getenv("QUERY_SERVICE_URL", "http://query_service:8000")
DOWNLOAD_SERVICE_URL = os.getenv("DOWNLOAD_SERVICE_URL", "http://download_service:8000")


@router.post(
    "/upload",
    responses={
        400: {
            "description": "Bad Request. This can happen if no file is included or the file is not a valid video.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_file": {
                            "summary": "No file provided",
                            "value": {
                                "message": "You must include a video file in the request form-data."
                            },
                        },
                        "invalid_file_type": {
                            "summary": "File provided is not a video",
                            "value": {
                                "message": "Invalid file type. Only videos are allowed."
                            },
                        },
                    }
                }
            },
        }
    },
)
async def proxy_upload(req: Request):
    async with httpx.AsyncClient() as client:
        body = await req.body()

        headers = dict(req.headers)

        res = await client.post(
            f"{UPLOAD_SERVICE_URL}/upload", content=body, headers=headers
        )

        return Response(
            content=res.content,
            status_code=res.status_code,
            headers=res.headers,
            media_type=res.headers.get("content-type"),
        )


@router.get(
    "/status",
    responses={
        400: {
            "description": "Missing required parameter(s)",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Missing required parameter(s): user_id, transaction_id"
                    }
                }
            },
        }
    },
)
async def proxy_status(user_id: str, transaction_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{QUERY_SERVICE_URL}/status",
            params={"user_id": user_id, "transaction_id": transaction_id},
        )

        return Response(
            content=res.content,
            status_code=res.status_code,
            headers=res.headers,
            media_type=res.headers.get("content-type"),
        )


@router.get(
    "/download",
    responses={
        400: {
            "description": "Missing required parameter(s)",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Missing required parameter(s): user_id, transaction_id"
                    }
                }
            },
        }
    },
)
async def proxy_download(user_id: str, transaction_id: str):
    async with httpx.AsyncClient() as client:
        res = await client.get(
            f"{DOWNLOAD_SERVICE_URL}/download",
            params={"user_id": user_id, "transaction_id": transaction_id},
        )

        return Response(
            content=res.content,
            status_code=res.status_code,
            headers=res.headers,
            media_type=res.headers.get("content-type"),
        )
