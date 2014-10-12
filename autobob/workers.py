import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()


def regex_worker(matchq):
    while True:
        matcher, message = regexq.get()
        LOG.debug('Trying match with regex /{}/'.format(matcher.pattern))

        if matcher.pattern.match(message):
            matchq.put((matcher.priority, matcher.callback))

        regexq.task_done()
