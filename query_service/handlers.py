from fastapi import APIRouter, HTTPException

from db.connection import get_connection, release_connection

router = APIRouter()

@router.get("/status")
async def get_status(user_id: str, transaction_id: str):
    conn = get_connection()

    try:
        # get transaction from DB
        cur = conn.cursor()

        cur.execute(
            """
            SELECT transaction_id, user_id, filename, original_format, original_codec, target_format, target_codec, status, start_time, updated_time
            FROM transactions
            WHERE transaction_id = %s
            """,
            (transaction_id,)
        )

        row = cur.fetchone()
        cur.close()

        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        db_transaction_id, db_user_id, filename, original_format, original_codec, target_format, target_codec, status, start_time, updated_time = row
        
        # check that user_id provided matches user_id of transaction
        if db_user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        return {
            "transaction_id": db_transaction_id,
            "user_id": db_user_id,
            "filename": filename,
            "original_format": original_format, 
            "original_codec": original_codec, 
            "target_format": target_format, 
            "target_codec": target_codec,
            "status": status,
            "start_time": start_time, 
            "updated_time":updated_time
        }

    finally:
        release_connection(conn)