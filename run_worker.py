# Taken from https://python-rq.org/patterns/ and modified to suit my needs
from redis import Redis
from rq import Queue, Connection
from rq.worker import HerokuWorker as Worker
from decouple import config

listen = ["high", "default", "low"]

host = config("REDIS_HOST", None)
password = config("REDIS_PASSWORD", None)
port = config("REDIS_PORT", None)

if not host or not password or not port:
    raise RuntimeError("run_worker.py: Must configure environment variables.")

conn = Redis(host=host, password=password, port=port, ssl=True, ssl_cert_reqs=None)

if __name__ == "__main__":
    with Connection(conn):
        worker = Worker(map(Queue, listen))
        worker.work()
