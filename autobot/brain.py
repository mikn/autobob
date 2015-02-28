import queue
import logging
import datetime

LOG = logging.getLogger(__name__)

import autobot
from . import workers

catchalls = []
matchers = []
matchq = queue.PriorityQueue()
messageq = queue.Queue()
thread_pool = []


def boot(factory):
    global thread_pool
    storage = factory.get_storage()

    thread_pool = workers.init_threads(workers.regex_worker, (matchq,))
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
    workers.shutdown_pool(thread_pool, workers.regexq)
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
        storage['_internal']['last_error'] = {'timestamp': datetime.time(),
                                              'exception': e}
        message.reply('Ouch! That went straight to the brain! '
                      'Judging by the mechanics involved it will '
                      'probably happen if you try again as well... '
                      'so please don\'t...')
