import os
from redis import Redis
from rq import Queue


def enqueue_conversion_task(transaction_id: str, input_path: str, output_path: str):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_conn = Redis(host=redis_host)

    # increase queue timeout to 1 hour (3600s)
    q = Queue(connection=redis_conn, default_timeout=3600)

    q.enqueue(
        "tasks.convert_video.convert_video",
        transaction_id,
        input_path,
        output_path,
    )
