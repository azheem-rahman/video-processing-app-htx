import os
import uuid
from datetime import datetime

from fastapi import APIRouter, File, UploadFile, HTTPException

from db.db import get_connection, release_connection
from utils.get_video_codec import get_video_codec
from utils.enqueue import enqueue_conversion_task

router = APIRouter()
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    # check that file is a video
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only videos are allowed.")
    
    # save uploaded video to /uploads folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())

    # create transaction in DB
    conn = get_connection()
    try:
        cur = conn.cursor()

        transaction_id = str(uuid.uuid4())
        user_id = os.getenv("DEFAULT_USER_ID")
        codec = get_video_codec(file_path)

        cur.execute(
            """
            INSERT INTO transactions (
                transaction_id, user_id, filename, stored_path_original, original_format, 
                original_codec, target_format, target_codec, status, start_time, updated_time
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                transaction_id,
                user_id,
                file.filename,
                file_path,
                file.filename.split(".")[-1],
                codec,
                "mp4", # set target_format to "mp4" default for now, can change dynamically according to user's req later
                "h265",
                "Pending",
                datetime.now(),
                datetime.now()
            )
        )
        conn.commit()
        cur.close()
    finally:
        release_connection(conn)

    # queue task to Convert Service
    output_filename = f"{transaction_id}_{file.filename}"
    output_path = os.path.join("converted", output_filename)
    enqueue_conversion_task(transaction_id, file_path, output_path)
    
    return {"message": "File uploaded successfully", "filename": file.filename}