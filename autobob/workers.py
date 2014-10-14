import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()


def regex_worker(matchq):
    while True:
        matcher, message = regexq.get()
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))

        # We defer the condition matching to the workers knowing that it is
        # slightly more expensive. It is under the hopes that the loss of
        # performance is offset by the gain of threading
        if matcher.condition(message) and matcher.pattern.match(str(message)):
            LOG.debug('Match found against {}!'.format(matcher.pattern))
            matchq.put((matcher.prio, matcher))

        regexq.task_done()
