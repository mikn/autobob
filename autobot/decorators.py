import logging
import croniter

import autobot
from . import brain
from . import scheduler

LOG = logging.getLogger(__name__)


def eavesdrop(always=False, priority=1000):
    '''
    Always receive messages. Set priority to autobot.PRIORITY_ALWAYS if you
    want to catch all messages no matter if there is another match or not.
    '''
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        func._attach_class = True
        func._priority = priority
        callback = autobot.Callback(func)
        brain.catchalls.append(callback)
        return func
    return wrapper


def respond_to(pattern, always=False, priority=30):
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        def condition(message):
            return message.mentions_self()

        matcher = autobot.Matcher(func,
                                  pattern,
                                  priority=priority,
                                  condition=condition)
        _pattern_handler(matcher)
        return func
    return wrapper


def hear(pattern, always=False, priority=50):
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        matcher = autobot.Matcher(func, pattern, priority=priority)
        _pattern_handler(matcher)
        return func
    return wrapper


def _pattern_handler(matcher):
    matcher._func._attach_class = True
    brain.matchers.append(matcher)
    LOG.debug('Adding pattern: {} as a matcher'.format(matcher.pattern))


def randomly(func,
             times_per_day=1,
             day_of_week='*',
             start_time='00:00',
             end_time='23:59'):
    pass


def scheduled(minutes='*',
              hours='*',
              day_of_month='*',
              month='*',
              day_of_week='*',
              cron_str=None):
    def wrapper(func):
        cron_str = '{} {} {} {} {}'.format(
            minutes,
            hours,
            day_of_month,
            month,
            day_of_week
        )
        func._attach_class = True
        cron = croniter.croniter(cron_str)
        callback = autobot.ScheduledCallback(func, cron)
        scheduler.scheduleq.put(callback)
        return func
    return wrapper
