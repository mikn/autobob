import queue
import logging
import datetime

import autobot
from . import workers
from autobot import event

LOG = logging.getLogger(__name__)


class Brain(object):
    def __init__(self, factory, matchers, catchalls, messageq, workq):
        self._factory = factory
        self.matchers = matchers
        self.catchalls = catchalls
        self._messageq = messageq
        self._workq = workq
        self._dirty_substitutions = False
        self._matchq = queue.PriorityQueue()

    def boot(self):
        LOG.debug('Booting brain!')
        event.register(event.SERVICE_STARTED, self._compile_regexps)
        event.register(event.MESSAGE_RECEIVED, self._compile_regexps)
        event.register(event.SUBSTITUTIONS_ALTERED, self._track_substitutions)

        storage = self._factory.get_storage()
        while True:
            message = self._messageq.get()
            if type(message) is not autobot.Message:
                if not message:
                    LOG.info('Shutting down brain thread...')
                    self._messageq.task_done()
                    break
                LOG.warning('Found object in message queue that was not a '
                            'message at all! Type: %s', type(message))
                continue
            event.trigger(event.MESSAGE_RECEIVED, self)

            LOG.debug('Processing message: %s', message)
            LOG.debug('Number of matchers: %s', len(self.matchers))

            for matcher in self.matchers:
                work = workers.regex_work(matcher, message, self._matchq)
                self._workq.put(work)

            for callback in self.catchalls:
                self._matchq.put((callback.priority, callback))

            self._workq.join()  # This is mixed with schedule work

            self.run_callbacks(self._factory, storage, message)

            storage.sync()
            self._messageq.task_done()
            LOG.debug('Processing done!')

        storage.close()

    def shutdown(self):
        self._messageq.put(False)
        self._messageq.join()

    def run_callbacks(self, factory, storage, message):
        try:
            while True:
                priority, matcher = self._matchq.get_nowait()
                LOG.debug('Priority: %s Matcher: %s', priority, matcher)
                callback = matcher.get_callback(factory)
                callback(message)
                if priority <= autobot.PRIORITY_ALWAYS:
                    continue
                with self._matchq.mutex:
                    self._matchq.queue.clear()
        except ImportError:
            LOG.warning('Removing matcher with regex %s and method: %s from '
                        'class %s because it broke.',
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
