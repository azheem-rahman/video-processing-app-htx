from fastapi import APIRouter, Request, Response, Query
from uuid import UUID
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
            "description": "Bad Request. This can happen if no file is included, the file is not a video, or if user_id param is not provided or not a valid UUID.",
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
                        "missing_required_parameter": {
                            "summary": "user_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): user_id"
                            },
                        },
                        "parameter_not_UUID": {
                            "summary": "user_id provided is not a valid uuid",
                            "value": {
                                "message": "Invalid UUID format for parameter: user_id"
                            },
                        },
                    }
                }
            },
        }
    },
)
async def proxy_upload(req: Request, user_id: UUID = Query(...)):
    async with httpx.AsyncClient() as client:
        body = await req.body()
        headers = dict(req.headers)
        params = req.query_params

        res = await client.post(
            f"{UPLOAD_SERVICE_URL}/upload", content=body, headers=headers, params=params
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
            "description": "Bad Request. This can happen if required parameter(s) are not provided or if parameter(s) provided are not valid UUIDs.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_required_parameter_user_id": {
                            "summary": "user_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): user_id"
                            },
                        },
                        "missing_required_parameter_transaction_id": {
                            "summary": "transaction_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): transaction_id"
                            },
                        },
                        "missing_required_parameters": {
                            "summary": "user_id and transaction_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): user_id, transaction_id"
                            },
                        },
                        "parameter_not_UUID": {
                            "summary": "param provided is not a valid uuid",
                            "value": {
                                "message": "Invalid UUID format for parameter: '{param}'"
                            },
                        },
                    }
                }
            },
        }
    },
)
async def proxy_status(user_id: UUID = Query(...), transaction_id: UUID = Query(...)):
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
            "description": "Bad Request. This can happen if required parameter(s) are not provided.",
            "content": {
                "application/json": {
                    "examples": {
                        "missing_required_parameter_user_id": {
                            "summary": "user_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): user_id"
                            },
                        },
                        "missing_required_parameter_transaction_id": {
                            "summary": "transaction_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): transaction_id"
                            },
                        },
                        "missing_required_parameters": {
                            "summary": "user_id and transaction_id param not provided",
                            "value": {
                                "message": "Missing required parameter(s): user_id, transaction_id"
                            },
                        },
                        "parameter_not_UUID": {
                            "summary": "param provided is not a valid uuid",
                            "value": {
                                "message": "Invalid UUID format for parameter: '{param}'"
                            },
                        },
                    }
                }
            },
        }
    },
)
async def proxy_download(user_id: UUID = Query(...), transaction_id: UUID = Query(...)):
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
