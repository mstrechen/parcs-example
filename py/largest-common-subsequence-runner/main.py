import os
import random
import logging
import string
from contextlib import contextmanager

from parcs.server import Runner, serve
from functools import reduce
from time import time_ns


@contextmanager
def timed(name):
    begin = time_ns()
    logging.info(f"{name}: started")
    yield
    end = time_ns()
    diff_seconds = (end - begin) / (10**9)
    logging.info(f"{name}: finished in {diff_seconds}")


def generate_random_seq(length: int, alphabet: str = string.ascii_letters, seed: str = None):
    rand = random.Random(seed)
    return ''.join(rand.choice(alphabet) for _ in range(length))


def lcss_simple(s, t):
    n = len(s)
    m = len(t)
    res = [
        [0] * (m + 1)
        for _ in range(n + 1)
    ]
    for i in range(n):
        for j in range(m):
            res[i + 1][j + 1] = max(res[i][j + 1], res[i + 1][j]) if s[i] != t[j] else res[i][j] + 1
    return res[-1][1:]


def lcss_simple_full(s, t):
    res = []
    for suffix_i in range(len(t)):
        res.append([0] * suffix_i + lcss_simple(s, t[suffix_i:]))
    return res


def get_join_result(size):
    def join_result(res1, res2):
        return [
            [
                (
                    max(
                        res1[l][mid] + res2[mid + 1][r]
                        if mid != r
                        else res1[l][r]
                        for mid in range(l, r + 1)
                    )
                    if l <= r else
                    0
                 )
                for r in range(size)
            ]
            for l in range(size)
        ]
    return join_result


def split_tasks(s: str, n_workers: int):
    n = len(s)
    chunk_size = n // n_workers + (n % n_workers != 0)  # ceil
    for chunk_begin in range(0, n, chunk_size):
        yield s[chunk_begin:chunk_begin + chunk_size]


class LCSS(Runner):
    def run(self):
        seed = os.getenv('SEED')
        n = int(os.getenv('N', 100000))
        m = int(os.getenv('M', 30))
        workers = int(os.getenv('WORKERS', 2))

        logging.info(f'Got N = {n}, M = {m}, workers = {workers} from env vars')

        with timed('Generating samples'):
            s = generate_random_seq(n, alphabet=string.ascii_letters, seed=seed)
            t = generate_random_seq(m, alphabet=string.ascii_letters + string.digits, seed=seed)

        with timed('Sending task data'):
            tasks = []
            for substring in split_tasks(s, workers):
                task = self.engine.run('mstrechen/largest-common-subseqence-worker-go')
                task.send_all(substring, t)
                tasks.append(task)
            results = []

        with timed('Receiving partial results'):
            for task in tasks:
                partial_result = task.recv()
                logging.info(f'Computation time spent on worker: {partial_result["ExecutionTime"]}')
                results.append(partial_result['Result'])
            for task in tasks:
                task.shutdown()
        if m < 20:
            for partial_result, i in zip(results, range(len(results))):
                logging.info(f"==== PARTIAL RESULT {i} ====")
                for level in partial_result:
                    logging.info(level)
        with timed('Joining partial results, creating final result'):
            result = reduce(get_join_result(m), results)

        logging.info(f'==== MERGED RESULT ====')
        if m < 50:
            for level in result:
                logging.info(level)
        else:
            logging.info("Too long, just trust me")

serve(LCSS())
