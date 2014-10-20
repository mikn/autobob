import logging
import queue
LOG = logging.getLogger(__name__)

regexq = queue.Queue()


def regex_worker(matchq):
    leave = True
    while not leave:
        try:
            leave = regex_loop(matchq)
        except Exception as e:
            LOG.warning('Something broke horribly, which is a bit sad. '
                        'Error message I received was {}...'
                        'Resurrecting thread!'.format(e))


def regex_loop(matchq):
    while True:
        data = regexq.get()
        if not data:
            regexq.task_done()
            return True
        matcher, message = data
        LOG.debug('Trying match with regex {}'.format(matcher.pattern))

        # We defer the condition matching to the workers knowing that it is
        # slightly more expensive. It is under the hopes that the loss of
        # performance is offset by the gain of threading
        if matcher.condition(message) and matcher.pattern.match(str(message)):
            LOG.debug('Match found against {}!'.format(matcher.pattern))
            matchq.put((matcher.priority, matcher))

        regexq.task_done()
