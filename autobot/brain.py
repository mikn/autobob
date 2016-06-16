import queue
import logging
import datetime

LOG = logging.getLogger(__name__)

import autobot
from . import workers
from . import helpers
from autobot import event

catchalls = []
matchers = []
matchq = queue.PriorityQueue()
messageq = queue.Queue()


class Brain(object):
    def __init__(self, factory, matchers):
        self.matchers = matchers
        self._factory = factory
        self.thread_pool = []
        self._dirty_substitutions = False

    def boot(self):
        LOG.debug('Booting brain!')
        event.register(event.SERVICE_STARTED, self._compile_regexps)
        event.register(event.MESSAGE_RECEIVED, self._compile_regexps)
        event.register(event.SUBSTITUTIONS_ALTERED, self._track_substitutions)

        storage = self._factory.get_storage()
        self.thread_pool = workers.init_threads(workers.regex_worker, (matchq,))
        while True:
            message = messageq.get()
            if type(message) is not autobot.Message:
                if not message:
                    LOG.info('Shutting down brain thread...')
                    messageq.task_done()
                    break
                LOG.warning('Found object in message queue that was not a '
                            'message at all! Type: %s', type(message))
                continue
            event.trigger(event.MESSAGE_RECEIVED, self)

            LOG.debug('Processing message: %s', message)
            LOG.debug('Number of matchers: %s', len(self.matchers))

            for matcher in self.matchers:
                workers.regexq.put((matcher, message))

            for callback in catchalls:
                matchq.put((callback.priority, callback))

            workers.regexq.join()

            self.run_callbacks(self._factory, storage, message)

            storage.sync()
            messageq.task_done()
            LOG.debug('Processing done!')

        storage.close()


    def shutdown(self):
        workers.shutdown_pool(self.thread_pool, workers.regexq)
        messageq.put(False)
        messageq.join()


    def run_callbacks(self, factory, storage, message):
        try:
            while True:
                priority, matcher = matchq.get_nowait()
                LOG.debug('Priority: %s Matcher: %s', priority, matcher)
                callback = matcher.get_callback(factory)
                callback(message)
                if priority <= autobot.PRIORITY_ALWAYS:
                    continue
                with matchq.mutex:
                    matchq.queue.clear()
        except ImportError:
            LOG.warning('Removing matcher with regex %s and method: %s from class '
                        '%s because it broke, and I don\'t like rude toys.',
                            matcher.pattern,
                            matcher._func.__name__,
                            matcher.__func__._class_name)
            del(self.matchers[self.matchers.index(matcher)])
        except queue.Empty:
            pass
        except Exception as e:
            # TODO: This breaks with "no .find() on builtin object or method"
            LOG.error(e)
            now = datetime.datetime.now()
            storage['_internal']['last_error'] = {'timestamp': now,
                                                  'exception': e}
            message.reply('Ouch! That went straight to the brain! '
                          'Judging by the mechanics involved it will '
                          'probably happen if you try again as well... '
                          'so please don\'t...')

    def _track_substitutions(self, context, event_args):
        self._dirty_substitutions = True

    def _compile_regexps(self, context, event_args):
        if isinstance(context, autobot.Service) or self._dirty_substitutions:
            LOG.debug('Compiling regex with substitutions: %s',
                      autobot.substitutions)
            [m.compile(**autobot.substitutions) for m in self.matchers]
            self._dirty_substitutions = False
