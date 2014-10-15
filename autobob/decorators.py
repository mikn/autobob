import functools
import logging

import autobob
import autobob.brain

LOG = logging.getLogger(__name__)


def listen(always=False, priority=100):
    '''
    Listen on all messages. If `always` is True, the method will
    always run no matter if there are other matches or not.
    If `always` is false, it will run according to the value of priority
    where lower values are higher priority.
    '''
    def wrapper(func):
        func._attach_class = True
        func._priority = priority
        autobob.brain.catchalls.append((func, always))
        return func
    return wrapper


def respond_to(pattern, priority=30):
    def wrapper(func):
        cond = lambda m: m.mentions_self()
        matcher = autobob.Matcher(func, pattern, prio=priority, condition=cond)
        _pattern_handler(matcher)
        return func
    return wrapper


def hear(pattern, priority=50):
    def wrapper(func):
        matcher = autobob.Matcher(func, pattern, prio=priority)
        _pattern_handler(matcher)
        return func
    return wrapper


def _pattern_handler(matcher):
    matcher._func._attach_class = True
    autobob.brain.matchers.append(matcher)
    LOG.debug('Adding pattern: {} for as a matcher'.format(matcher.pattern))


def randomly(func,
             times_per_day=1,
             day_of_week='*',
             start_time='00:00',
             end_time='23:59'):
    pass


def scheduled(func,
              minutes='*',
              hours='*',
              day_of_month='*',
              month='*',
              day_of_week='*',
              cron_syntax=None):
    pass
