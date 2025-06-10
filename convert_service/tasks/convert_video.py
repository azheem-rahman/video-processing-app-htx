import os
import subprocess
from datetime import datetime
from db.connection import get_connection, release_connection

def convert_video(transaction_id, input_path, output_path):
    # check output directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conn = get_connection()

    try:
        cur = conn.cursor()

        # update transaction as "Converting"
        cur.execute(
            """
            UPDATE transactions
            SET status = %s, updated_time = %s
            WHERE transaction_id = %s
            """,
            ("Converting", datetime.now(), transaction_id)
        )
        conn.commit()

        # run ffmpeg to convert to H.265 codec in mp4 container
        result = subprocess.run(
            [
                "ffmpeg",           # run ffmpeg command
                "-i", input_path,   # set input file
                "-c:v", "libx265",  # convert video stream to H.265 (HEVC) codec
                "-tag:v", "hvc1",   # ensure compatibility with Apple/macOS
                output_path         # output file path (.mp4 container by default)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True
        )

        if result.returncode == 0:
            # update transaction as "Completed" if conversion executed successfully
            cur.execute(
                """
                UPDATE transactions
                SET status = %s, stored_path_converted = %s, updated_time = %s
                WHERE transaction_id = %s
                """,
                ("Completed", output_path, datetime.now(), transaction_id)
            )
        else:
            print("FFmpeg failed with error:")
            print(result.stderr.decode())
            # update transaction as "Failed" if conversion not executed successfully
            cur.execute(
                """
                UPDATE transactions
                SET status = %s, updated_time = %s
                WHERE transaction_id = %s
                """,
                ("Failed", datetime.now(), transaction_id)
            )

        conn.commit()
        cur.close()
    finally:
        release_connection(conn)