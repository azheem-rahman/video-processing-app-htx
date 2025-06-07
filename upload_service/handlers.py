from fastapi import APIRouter, File, UploadFile, HTTPException
import os

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
    
    return {"message": "File uploaded successfully", "filename": file.filename}