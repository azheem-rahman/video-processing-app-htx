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
            SELECT transaction_id, user_id, filename, status, stored_path_converted 
            FROM transactions
            WHERE transaction_id = %s
            """,
            (transaction_id,)
        )

        row = cur.fetchone()
        cur.close()

        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        db_transaction_id, db_user_id, filename, status, converted_path = row
        # check that user_id provided matches user_id of transaction
        if db_user_id != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")

        return {
            "transaction_id": db_transaction_id,
            "user_id": db_user_id,
            "filename": filename,
            "status": status,
            "converted_path": converted_path
        }

    finally:
        release_connection(conn)