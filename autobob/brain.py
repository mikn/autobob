import multiprocessing
import queue
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


def boot(factory):
    thread_pool = init_threads(autobob.workers.regex_worker, (matchq,))

    while True:
        relevant_matchers = []
        message = messageq.get()
        LOG.debug('Processing message: {}'.format(message))
        if type(message) is not autobob.robot.Message:
            LOG.warning('Found object in message queue that was not a '
                        'message at all! Type: {}'.format(type(message)))
            continue
        relevant_matchers.extend(matchers)
        if message.mentions('botname'):
            LOG.debug('Adding in metion matchers since we found botname')
            relevant_matchers.extend(mention_matchers)

        LOG.debug('Number of matchers: {}'.format(len(relevant_matchers)))

        for matcher in relevant_matchers:
            autobob.workers.regexq.put((matcher, str(message)))

        for callback in catchalls:
            matchq.put((100, callback))

        autobob.workers.regexq.join()

        try:
            _, matcher = matchq.get_nowait()
            callback = matcher.get_callback(factory)
            callback(message)
            with matchq.mutex:
                matchq.queue.clear()
        except queue.Empty:
            pass
        except Exception as e:
            LOG.error(e)
            # We probably want to print the debug in the "home" channel
            # and perhaps a "sorry" where the message came from unless admin
            pass

        messageq.task_done()
        LOG.debug('Processing done!')
