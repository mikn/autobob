import functools
import logging

import autobob.brain
import autobob.robot

LOG = logging.getLogger(__name__)


def always(func):
    autobob.brain.catchalls.append(func)
    return func


# Important to remember that the funcs here are CLASS methods
# Should probably get the class from the factory before passing it into
# the matcher object
def respond_to(pattern):
    def wrapper(func):
        return _pattern_handler(func, pattern, autobob.brain.matchers)
    return wrapper


def hear(pattern):
    def wrapper(func):
        return _pattern_handler(func, pattern, autobob.brain.matchers)
    return wrapper


def _pattern_handler(func, pattern, matchers):
    func.attach_class = True
    matcher = autobob.robot.Matcher(func, pattern)
    matchers.append(matcher)
    LOG.debug('Adding pattern: {} for as a matcher'.format(pattern))
    return func


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
