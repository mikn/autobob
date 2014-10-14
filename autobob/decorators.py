import functools
import logging

import autobob
import autobob.brain

LOG = logging.getLogger(__name__)


def always(func):
    func.attach_class = True
    autobob.brain.catchalls.append(func)
    return func


def listen(func):
    pass


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
    matcher._func.attach_class = True
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


def plugin(cls):
    LOG.debug('Iterating over class {}'.format(cls))
    for name, method in cls.__dict__.items():
        if hasattr(method, 'attach_class') and method.attach_class:
            setattr(method, 'class_name', cls.__name__)

    return cls
