import os
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from uuid import UUID

from db.connection import get_connection, release_connection

router = APIRouter()


@router.get("/download")
async def download(user_id: UUID = Query(...), transaction_id: UUID = Query(...)):
    conn = get_connection()

    try:
        # get transaction from DB
        cur = conn.cursor()

        cur.execute(
            """
            SELECT user_id, stored_path_converted, status
            FROM transactions
            WHERE transaction_id = %s
            """,
            (str(transaction_id),),
        )

        row = cur.fetchone()
        cur.close()

        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")

        db_user_id, stored_path_converted, status = row

        # check that user_id provided matches user_id of transaction
        if db_user_id != str(user_id):
            raise HTTPException(status_code=403, detail="Forbidden")

        # check that status is "Completed" and stored_path_converted is not null
        if status != "Completed" or not stored_path_converted:
            raise HTTPException(status_code=409, detail="File not ready for download")

        # check file exists on disk
        if not os.path.isfile(stored_path_converted):
            raise HTTPException(status_code=500, detail="Converted file missing")

        return FileResponse(
            stored_path_converted,
            media_type="application/octet-stream",
            filename=os.path.basename(stored_path_converted),
        )

    finally:
        release_connection(conn)
