import os
from redis import Redis
from rq import Queue
from tasks.convert_video import convert_video

def enqueue_conversion_task(transaction_id: str, input_path: str, output_path: str):
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_conn = Redis(host=redis_host)
    q = Queue(connection=redis_conn)
    q.enqueue(convert_video, transaction_id, input_path, output_path)