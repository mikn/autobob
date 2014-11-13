import multiprocessing
import queue
import threading
import logging

LOG = logging.getLogger(__name__)

import autobot
from . import workers

catchalls = []
matchers = []
matchq = queue.PriorityQueue()
messageq = queue.Queue()
thread_pool = []


def init_threads(worker, args):
    pool = []
    try:
        thread_count = multiprocessing.cpu_count()*2
    except NotImplementedError:
        thread_count = 4

    LOG.debug('Setting thread count to: {}.'.format(thread_count))

    for i in range(thread_count):
        thread_name = 'regex_worker-{}'.format(i+1)
        t = threading.Thread(name=thread_name, target=worker, args=args)
        pool.append(t)
        t.start()

    return pool


def boot(factory):
    global thread_pool
    storage = factory.get_storage()

    thread_pool = init_threads(workers.regex_worker, (matchq,))
    while True:
        message = messageq.get()
        if type(message) is not autobot.Message:
            if not message:
                LOG.info('Shutting down brain thread...')
                messageq.task_done()
                break
            LOG.warning('Found object in message queue that was not a '
                        'message at all! Type: {}'.format(type(message)))
            continue

        LOG.debug('Processing message: {}'.format(message))
        LOG.debug('Number of matchers: {}'.format(len(matchers)))

        for matcher in matchers:
            workers.regexq.put((matcher, message))

        for callback in catchalls:
            matchq.put((callback.priority, callback))

        workers.regexq.join()

        run_callbacks(factory, storage, message)

        storage.sync()
        messageq.task_done()
        LOG.debug('Processing done!')

    storage.close()


def shutdown():
    for thread in thread_pool:
        LOG.info('Closing thread {}'.format(thread.name))
        while thread.isAlive():
            workers.regexq.put(False)
            workers.regexq.join()
    messageq.put(False)
    messageq.join()


def run_callbacks(factory, storage, message):
    try:
        while True:
            priority, matcher = matchq.get_nowait()
            callback = matcher.get_callback(factory)
            callback(message)
            if priority <= autobot.PRIORITY_ALWAYS:
                continue
            with matchq.mutex:
                matchq.queue.clear()
    except ImportError:
        LOG.warning('Removing matcher with regex {} and method: {} from class '
                    '{} because it broke, and I don\'t like rude toys.'.format(
                        matcher.pattern,
                        matcher._func.__name__,
                        matcher.__func__._class_name))
        del(matchers[matchers.index(matcher)])
    except queue.Empty:
        pass
    except Exception as e:
        LOG.error(e)
        storage['_internal']['last_error'] = e
        message.reply('Ouch! That went straight to the brain! '
                      'Judging by the mechanics involved it will '
                      'probably happen if you try again as well... '
                      'so please don\'t...')
