from typing import Coroutine
from rq import Queue
from django_rq import get_queue


def periodic_job(func: Coroutine, period, queue="default"):
    queue = get_queue(queue=queue)
    first_job = queue.enqueue(func, )