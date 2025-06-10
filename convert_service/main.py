import os
from rq import Worker, Queue
from redis import Redis

if __name__ == '__main__':
    redis_host = os.getenv("REDIS_HOST", "localhost")
    redis_conn = Redis(host=redis_host)
    queues = [Queue("default", connection=redis_conn)]

    worker = Worker(queues=queues, connection=redis_conn)
    worker.work()