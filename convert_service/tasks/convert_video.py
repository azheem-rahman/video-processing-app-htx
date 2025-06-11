import os
import subprocess
from datetime import datetime

from db.connection import get_connection, release_connection


def convert_video(transaction_id: str, input_path: str, output_path: str):
    # create output directory if does not exist
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
            ("Converting", datetime.now(), transaction_id),
        )
        conn.commit()

        # set number of threads use to 2 or to (cpu_count() or fallback to 1 if cpu_count() returns None)
        num_threads = min(2, os.cpu_count() or 1)

        # run ffmpeg to convert to H.265 codec in mp4 container
        result = subprocess.run(
            [
                "ffmpeg",  # run ffmpeg command
                "-i",
                input_path,  # set input file
                "-preset",
                "ultrafast",  # set -preset to ultrafast to reduce encoding time
                "-threads",
                str(num_threads),  # set num of threads to use
                "-c:v",
                "libx265",  # convert video stream to H.265 (HEVC) codec
                "-tag:v",
                "hvc1",  # ensure compatibility with Apple/macOS
                output_path,  # output file path (.mp4 container by default)
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            start_new_session=True,
        )

        if result.returncode == 0:
            # update transaction as "Completed" if conversion executed successfully
            cur.execute(
                """
                UPDATE transactions
                SET status = %s, stored_path_converted = %s, updated_time = %s
                WHERE transaction_id = %s
                """,
                ("Completed", output_path, datetime.now(), transaction_id),
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
                ("Failed", datetime.now(), transaction_id),
            )

        conn.commit()
        cur.close()

    except Exception as e:
        print(f"Error during conversion: {e}")
        error_msg = str(e)

        try:
            cur = conn.cursor()

            cur.execute(
                """
                UPDATE transactions
                SET status = %s, error_reason = %s, updated_time = %s
                WHERE transaction_id = %s
                """,
                ("Failed", error_msg, datetime.now(), transaction_id),
            )

            conn.commit()
            cur.close()

        except Exception as update_error:
            print(f"Failed to update DB status to '{error_msg}': {update_error}")

    finally:
        release_connection(conn)
