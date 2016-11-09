import threading
import multiprocessing
import logging

LOG = logging.getLogger(__name__)


def schedule_work(func):
    return func


def regex_work(matcher, message, matchq):
    def processor():
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))
        # We defer the condition matching to the workers knowing that it is
        # slightly more expensive. It is under the hopes that the loss of
        # performance is offset by the gain of threading
        if matcher.condition(message):
            message.process(matcher.preprocessor)
            if matcher.regex.match(str(message)):
                LOG.debug('Match found against {}!'.format(matcher.pattern))
                matchq.put((matcher.priority, matcher))
    return processor


class WorkerPool(object):
    def __init__(self, workq, thread_count=None):
        self._workq = workq
        self._thread_pool = []
        self._thread_count = thread_count

    def start(self):
        try:
            if not self._thread_count or self._thread_count < 1:
                self._thread_count = multiprocessing.cpu_count()*2
        except NotImplementedError:
            self._thread_count = 4
        LOG.debug('Setting thread count to: {}.'.format(self._thread_count))

        for i in range(self._thread_count):
            thread_name = '{}-{}'.format('worker', i+1)
            t = threading.Thread(name=thread_name, target=self.worker)
            self._thread_pool.append(t)
            t.start()

    def worker(self):
        while True:
            work = self._workq.get()
            if not work or not callable(work):
                self._workq.task_done()
                return True
            work()
            self._workq.task_done()

    def shutdown(self):
        for thread in self._thread_pool:
            LOG.info('Closing thread %s', thread.name)
            while thread.isAlive():
                self._workq.put(False)
                self._workq.join()
