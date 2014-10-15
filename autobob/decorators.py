import functools
import logging

import autobob
import autobob.brain

LOG = logging.getLogger(__name__)


def always_listen(func):
    func._attach_class = True
    autobob.brain.catchalls.append(func)
    return func


def respond_to(pattern):
    def wrapper(func):
        cond = lambda m: m.mentions_self()
        matcher = autobob.Matcher(func, pattern, prio=40, condition=cond)
        _pattern_handler(matcher)
        return func
    return wrapper


def hear(pattern):
    def wrapper(func):
        matcher = autobob.Matcher(func, pattern)
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
