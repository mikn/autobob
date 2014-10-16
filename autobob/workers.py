import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()


def regex_worker(matchq):
    while True:
        data = regexq.get()
        if not data:
            regexq.task_done()
            break
        matcher, message = data
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))

        # We defer the condition matching to the workers knowing that it is
        # slightly more expensive. It is under the hopes that the loss of
        # performance is offset by the gain of threading
        if matcher.condition(message) and matcher.pattern.match(str(message)):
            LOG.debug('Match found against {}!'.format(matcher.pattern))
            matchq.put((matcher.priority, matcher))

        regexq.task_done()
