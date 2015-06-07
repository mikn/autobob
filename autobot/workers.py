import threading
import multiprocessing
import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()
callbackq = queue.Queue()


def regex_worker(matchq):
    while True:
        data = regexq.get()
        if not data or not len(data) == 2:
            regexq.task_done()
            return True
        matcher, message = data
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))

        # We defer the condition matching to the workers knowing that it is
        # slightly more expensive. It is under the hopes that the loss of
        # performance is offset by the gain of threading
        if matcher.condition(message):
            message.process(matcher.preprocessor)
            if matcher.regex.match(str(message)):
                LOG.debug('Match found against {}!'.format(matcher.pattern))
                matchq.put((matcher.priority, matcher))

        regexq.task_done()


def schedule_worker():
    while True:
        callback = callbackq.get()
        if not callback or not isinstance(callback, callable):
            callbackq.task_done()
            return True

        callback()
        callbackq.task_done()


def init_threads(worker, args, thread_count=None):
    pool = []
    try:
        if not thread_count or thread_count < 1:
            thread_count = multiprocessing.cpu_count()*2
    except NotImplementedError:
        thread_count = 4

    LOG.debug('Setting thread count to: {}.'.format(thread_count))

    for i in range(thread_count):
        thread_name = '{}-{}'.format(worker.__name__, i+1)
        t = threading.Thread(name=thread_name, target=worker, args=args)
        pool.append(t)
        t.start()

    return pool


def shutdown_pool(pool, queue):
    for thread in pool:
        LOG.info('Closing thread {}'.format(thread.name))
        while thread.isAlive():
            queue.put(False)
            queue.join()
