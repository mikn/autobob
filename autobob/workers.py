import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()


def regex_worker(matchq):
    while True:
        matcher, message = regexq.get()
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))

        if matcher.condition(message) and matcher.pattern.match(str(message)):
            LOG.debug('Match found against {}!'.format(matcher.pattern))
            matchq.put((matcher.prio, matcher))

        regexq.task_done()
