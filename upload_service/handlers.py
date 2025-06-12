import os
import uuid
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException, Query

from db.connection import get_connection, release_connection
from upload_service.utils.get_video_codec import get_video_codec
from upload_service.utils.enqueue import enqueue_conversion_task

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/upload")
async def upload_video(user_id: UUID = Query(...), file: UploadFile = File(...)):
    # check that file is a video
    if not file.content_type.startswith("video/"):
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only videos are allowed."
        )

    # save uploaded video to /storage/uploads folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # create transaction in DB
    conn = get_connection()

    try:
        cur = conn.cursor()

        generated_transaction_id = str(uuid.uuid4())
        codec = get_video_codec(file_path)

        cur.execute(
            """
            INSERT INTO transactions (
                transaction_id, user_id, filename, stored_path_original, original_format, 
                original_codec, target_format, target_codec, status, start_time, updated_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                generated_transaction_id,
                str(user_id),
                file.filename,
                file_path,
                file.filename.split(".")[-1],
                codec,
                "mp4",  # set target_format to "mp4" default for now, can change dynamically according to user's req later
                "h265",
                "Pending",
                datetime.now(),
                datetime.now(),
            ),
        )
        conn.commit()
        cur.close()

        # queue task to Convert Service
        output_filename = f"{generated_transaction_id}_{file.filename}"
        output_path = os.path.join("converted", output_filename)

        enqueue_conversion_task(generated_transaction_id, file_path, output_path)

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to process upload: ${str(e)}"
        )

    finally:
        release_connection(conn)

    return {
        "message": "File uploaded successfully",
        "filename": file.filename,
        "transaction_id": generated_transaction_id,
    }
