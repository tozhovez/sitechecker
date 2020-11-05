import sys
from redis import Redis
from rq import Queue


def flush():
    """


    Returns:
        None.

    """
    # Flush Redis
    print('Flushing Redis data...')
    redis_client = Redis(host='127.0.0.1', port=6379, db=0)
    redis_client.flushall()

    # Empty rq queues
    print('Clear rq queue...')
    q = Queue(connection=Redis(host='127.0.0.1', port=6379, db=0))
    q.empty()


if __name__ == '__main__':

    answer = input(
        "Are you sure you want to flush all dbs / cache and queues: (y/n) "
        )
    if answer == "y":
        flush()
    elif answer == "n":
        sys.exit(0)
    else:
        print("Please enter y or n.")
