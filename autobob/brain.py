import multiprocessing
import queue
import random
import threading
import logging

LOG = logging.getLogger(__name__)

import autobob.robot
import autobob.workers

catchalls = []
matchers = []
mention_matchers = []
matchq = queue.PriorityQueue()
messageq = queue.Queue()
thread_pool = []

def init_threads(workers, args):
    pool = []
    try:
        thread_count = multiprocessing.cpu_count()*2
    except NotImplementedError:
        thread_count = 4

    LOG.debug('Setting thread count to: {}.'.format(thread_count))

    for i in range(thread_count):
        t = threading.Thread(target=workers, args=args)
        pool.append(t)
        t.daemon = True
        t.start()

    return pool


def boot():
    thread_pool = init_threads(autobob.workers.regex_worker, (matchq,))

    while True:
        message = messageq.get()
        LOG.debug('Processing message: {}'.format(message))
        if type(message) is not autobob.robot.Message:
            LOG.warning('Found object in message queue that was not a '
                        'message at all! Type: {}'.format(type(message)))
            continue
        relevant_matchers = matchers
        if message.mentions('botname'):
            relevant_matchers.extend(mention_matchers)

        for matcher in relevant_matchers:
            workers.regexq.put(matcher)

        for callback in catchalls:
            matchq.put((100, callback))

        autobob.workers.regexq.join()

        try:
            callback = matchq.get_nowait()
            callback(message)
            with matchq.mutex:
                matchq.queue.clear()
        except queue.Empty:
            pass
        except Error as e:
            LOG.error(e)
            # We probably want to print the debug in the "home" channel
            # and perhaps a "sorry" where the message came from unless admin
            pass

        messageq.task_done()
        LOG.debug('Processing done!')
