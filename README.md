# HTX Backend Assessment (Video Processing Backend System)

This project is a containerised video processing backend system that supports file (video) uploads, asynchronous video codec convertion to H.265, and job status querying. Built using a microservices architecture.

## Table of Contents

- [Setup & Running the App](#setup--running-the-app)
- [Testing the App](#testing-the-app)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Services](#services)
- [Endpoints](#endpoints)
- [Error Handling](#error-handling)
- [Directory Structure](#directory-structure)
- [Learning Points](#learning-points)
- [Future Enhancements](#future-enhancements)

## Setup & Running the App

```bash
# Step 1: Clone the repo
$ git clone https://github.com/azheem-rahman/video-processing-app-htx.git

# Step 2: Start all services
$ docker-compose up --build

# To access Swagger
Open http://localhost:8000/docs

# To connect to DB using any DB manager GUI
Host: localhost
Port: 55432
User: postgres
Password: password
```

## Testing the App

```bash
1. Start all services (in detached mode):
   docker-compose up -d --build

2. Run the test script in one-off container and remove after finish:
   docker-compose run --rm test-runner

3. To view logs:
   docker-compose logs -f
```

## Tech Stack

| Tool/Library       | Role                                                                                   |
| ------------------ | -------------------------------------------------------------------------------------- |
| **FastAPI**        | Web framework for API endpoints and services                                           |
| **Starlette**      | Used internally by FastAPI (e.g. `JSONResponse`)                                       |
| **Redis + RQ**     | Message broker and queue for async jobs                                                |
| **PostgreSQL**     | Main database (exposed on port `55432`)                                                |
| **Uvicorn**        | ASGI server to run FastAPI apps                                                        |
| **httpx**          | Async HTTP client used in API Gateway                                                  |
| **psycopg2**       | PostgreSQL database driver                                                             |
| **FFmpeg**         | Video conversion tool for format conversion (ffmpeg) and metadata extraction (ffprobe) |
| **Docker Compose** | Service orchestration                                                                  |

## Architecture

![Architecture Diagram](/Architecture%20Diagram.jpg)

**Notes (not implemented but shown in diagram):**

1. Image Upload (POST /upload-image)

- Handled by Upload Service, reuse existing pipeline
- Differentiation made by endpoint path
- Image saved and processed e.g. compression, thumbnailing etc.
- Store image metadata in PostgreSQL DB

2. Video Stream (GET /stream)

- Managed by new Streaming Service
- Serves video content in a streaming-compatible format e.g. chunked mp4 from file system
- Avoids full downloads and enables buffered playback, ideal for large files
- Client -> API Gateway -> Streaming Service -> DB + File System -> Client

## Services

| Service              | Description                                                                       |
| -------------------- | --------------------------------------------------------------------------------- |
| **API Gateway**      | Entry point for clients (`http://localhost:8000`). Routes and validates requests. |
| **Upload Service**   | Receives video upload, saves to disk, logs job in DB, enqueues convert task.      |
| **Convert Service**  | Background worker using RQ that picks up jobs from Redis and runs FFmpeg.         |
| **Query Service**    | Retrieves job status based on `transaction_id` and `user_id`.                     |
| **Download Service** | Validates request and serves file download if file has completed conversion.      |
| **PostgreSQL**       | Stores transactions and metadata. Exposed on `localhost:55432` for inspection.    |
| **Redis**            | Message broker for queueing conversion jobs.                                      |

## Endpoints

| Endpoint    | Method | Description                        | Example Request                                                                                     | Success Response Example                                               |
| ----------- | ------ | ---------------------------------- | --------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------- |
| `/upload`   | POST   | Upload a video file for processing | Multipart/form-data with key `file`, and query param `user_id=45c0d605-4b1f-4aef-bc7a-0ff819c49398` | `{ "message": "File uploaded successfully", "transaction_id": "..." }` |
| `/status`   | GET    | Check conversion status            | `?user_id=45c0d605-4b1f-4aef-bc7a-0ff819c49398&transaction_id=2cb59033-712c-4a1c-96a3-a5feaf2ef691` | `{ "status": "Completed" }`                                            |
| `/download` | GET    | Download the converted video file  | `?user_id=45c0d605-4b1f-4aef-bc7a-0ff819c49398&transaction_id=2cb59033-712c-4a1c-96a3-a5feaf2ef691` | Binary video file (mp4)                                                |

**Notes:**

- All endpoints are served via the API Gateway at `http://localhost:8000`
- `user_id` must be passed manually as a query parameter in UUID format e.g. 45c0d605-4b1f-4aef-bc7a-0ff819c49398. This is a temporary setup to simulate authenticated users until user registration and login are implemented.
- `transaction_id` expected to be a valid UUID for `/status` and `/download` requests. Invalid UUIDs will return a Error 400 with a descriptive message.

## Error Handling

- **Validation Errors**:

  - If a video file is missing: `400` with message `You must include a video file in the request form-data.`
  - If wrong file type: `400` with message `Invalid file type. Only videos are allowed.`
  - If query parameters are missing: `400` with `Missing required parameter(s): ...`

- **Job Status Errors**:

  - `404` if `transaction_id` not found.
  - `409` if file not ready for download.
  - `500` if converted file is missing from disk.

> Note: Swagger UI is available at `http://localhost:8000/docs` (via API Gateway).

## Directory Structure

```
.
├── api_gateway/
│   ├── Dockerfile              # Docker config for API Gateway
│   ├── handlers.py             # defines proxy endpoints (/upload, /status, /download)
│   ├── main.py                 # starts FastAPI app and includes exception handler
│   └── requirements.txt        # dependencies for API Gateway
├── convert_service/
│   ├── tasks/
|   │   └── convert_video.py    # core logic to run FFmpeg conversion and update DB accordingly
│   ├── Dockerfile              # Docker config for Convert Service
│   ├── main.py                 # initialise RQ worker and listens for tasks from Redis queue
│   └── requirements.txt        # dependencies for Convert Service
├── db/
│   └── connection.py           # PostgreSQL connection pool shared across services
├── download_service/
│   ├── Dockerfile              # Docker config for Download Service
│   ├── handlers.py             # handles file download endpoint (/download)
│   ├── main.py                 # starts FastAPI app
│   └── requirements.txt        # dependencies for Download Service
├── query_service/
│   ├── Dockerfile              # Docker config for Query Service
│   ├── handlers.py             # handles file query endpoint (/status)
│   ├── main.py                 # starts FastAPI app
│   └── requirements.txt        # dependencies for Query Service
├── storage/
│   ├── converted/              # folder to store converted videos on local storage (auto-created if does not exist)
│   └── uploads/                # folder to store original uploaded videos on local storage (auto-created if does not exist)
├── upload_service/
│   ├── utils/
|   │   ├── enqueue.py          # helper function to enqueue task to Redis queue
|   │   └── get_video_codec.py  # helper function to get original codec using ffprobe
│   ├── Dockerfile              # Docker config for Upload Service
│   ├── handlers.py             # handles file upload endpoint (/upload)
│   ├── main.py                 # starts FastAPI app and includes exception handler
│   └── requirements.txt        # dependencies for Upload Service
├── .gitignore
├── Architecture Diagram.jpg
├── docker-compose.yml          # orchestration file to run all services
├── README.md
└── schema.sql                  # SQL schema to initialise PostgreSQL DB

```

## Learning Points

**Timeout behaviour**

- Initially attempted to set a timeout value directly in q.enqueue(...), it had no effect whether specified on producer, consumer, or both sides (timeout reverts to default 180s).
- What ultimately worked was setting defaut_timeout when instantiating the queue on the producer side e.g. Queue(connection=redis_conn, default_timeout=3600), before calling enqueue(...).
- This ensure all jobs in that queue get that set timeout.

**Queue vs Job timeout**

- Per-job timeouts allow fine-tuning based on file size but using a queue-wide timeout is safer.

**File Validation**

- FastAPI's built-in validation throws Error `422` for missing required fiels (file or params) before hitting handler — custom exception handler added to handle such scenario for easier debugging on client side.

**Docker Compose Networking**

- Service names act as internal DNS e.g. `upload_service:8000`

## Future Enhancements

- Implement authentication and user management
- Support multiple file uploads in a single request
- Restrict access to download/stream only for authorised users (currently, we only check if user_id provided matches the user_id linked to transaction found in DB)
- Show real-time conversion progress or job queue status
- Enable optional thumbnail or preview generation
- Support uploading to and downloading from cloud storage e.g. S3
- Autoscale
