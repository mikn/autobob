import multiprocessing
import queue
import threading
import logging

LOG = logging.getLogger(__name__)

import autobob
import autobob.workers

catchalls = []
matchers = []
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
        thread_name = 'regex_worker-{}'.format(i+1)
        t = threading.Thread(name=thread_name, target=workers, args=args)
        pool.append(t)
        t.start()

    return pool


def boot(factory):
    global thread_pool
    storage = factory.get_storage()

    thread_pool = init_threads(autobob.workers.regex_worker, (matchq,))
    while True:
        message = messageq.get()
        if type(message) is not autobob.Message:
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
            autobob.workers.regexq.put((matcher, message))

        # TODO: make compatible with get_callback pattern used below
        # TODO: warn if you have more than one, refer to @listen decorator
        for callback in catchalls:
            matchq.put((100, callback))

        autobob.workers.regexq.join()

        try:
            _, matcher = matchq.get_nowait()
            callback = matcher.get_callback(factory)
            callback(message)
            with matchq.mutex:
                matchq.queue.clear()
        except ImportError:
            LOG.warning('Removing matcher with regex {} and method: {}. I can '
                        'however not tell you which class it comes from...'
                        ''.format(matcher.pattern, matcher._func.__name__))
            del(matchers[matchers.index(matcher)])
        except queue.Empty:
            pass
        except Exception as e:
            LOG.error(e)
            # TODO: We probably want to print the debug in the "home" channel
            # and perhaps a "sorry" where the message came from unless admin
            pass

        storage.sync()
        messageq.task_done()
        LOG.debug('Processing done!')

    storage.close()

def shutdown():
    for thread in thread_pool:
        LOG.info('Closing thread {}'.format(thread.name))
        while thread.isAlive():
            autobob.workers.regexq.put(False)
            autobob.workers.regexq.join()
    messageq.put(False)
    messageq.join()
