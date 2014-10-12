import functools
import logging

LOG = logging.getLogger(__name__)

import autobob.brain
import autobob.robot


def always(func):
    autobob.brain.catchalls.append(func)
    return func


# Important to remember that the funcs here are CLASS methods
# Should probably get the class from the factory before passing it into
# the matcher object
def respond_to(pattern):
    def _dec(func):
        def capture(*args, **kwargs):
            return func(*args, **kwargs)
        if not hasattr(func, 'patterns'):
            func.patterns = []
        func.patterns.append((pattern, True))
        return func
    return _dec


def hear(pattern):
    def _dec(func):
        def capture(*args, **kwargs):
            return func(*args, **kwargs)
        if not hasattr(func, 'patterns'):
            func.patterns = []
        func.patterns.append((pattern, False))
        return func
    return _dec


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
        if not hasattr(method, 'patterns'):
            continue
        setattr(method, 'class_name', cls.__name__)
        setattr(method, 'func_name', name)
        for pattern, mentions in method.patterns:
            matcher = autobob.robot.Matcher(method, pattern)
            if mentions:
                autobob.brain.mention_matchers.append(matcher)
            else:
                autobob.brain.mention.append(matcher)

            LOG.debug('Adding pattern: {} for as a matcher'.format(pattern))

    return cls
