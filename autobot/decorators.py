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
    '''
    The methods decorated with this one is supposed to only respond to direct
    messages to the bot/mentions and not general listening.  It does this by
    using the mentions_self() method on the message object as a matcher
    condition.
    It provides a format string of {mention_name} which will be replaced with
    the configured mention name at regexp compile time.
    If you do not set this within the string, it will be matched against the
    messsage received with the mention name already stripped from the beginning
    of the message.
    Thus, the default match without {mention_name} in the string becomes:
    ({mention_name}:?\s*)(pattern). Since the mention name gets stripped from
    the matched string, you can still anchor your pattern to the beginning of
    the string.
    This method also matches all messages received in private chats.
    '''
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        def condition(message):
            return message.mentions_self() or message.direct_message()

        matcher = autobot.Matcher(func,
                                  pattern,
                                  priority=priority,
                                  condition=condition)
        _pattern_handler(matcher)
        return func
    return wrapper


def hear(pattern, always=False, priority=50):
    '''
    It will match the pattern provided against all messages processed.
    '''
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        matcher = autobot.Matcher(func, pattern, priority=priority)
        _pattern_handler(matcher)
        return func
    return wrapper


def subscribe_to(event):
    def wrapper(func):
        callback = autobot.Callback(func)
        func._attach_class = True
        autobot.event.register(event, callback)
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
