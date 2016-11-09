import logging
import croniter
from datetime import datetime

import autobot

LOG = logging.getLogger(__name__)


def eavesdrop(always=False, priority=1000):
    '''
    Always receive messages. Set priority to autobot.PRIORITY_ALWAYS if you
    want to catch all messages no matter if there is another match or not.
    '''
    if always:
        priority = autobot.PRIORITY_ALWAYS

    def wrapper(func):
        func._priority = priority
        callback = autobot.Callback(func)
        _add_callback(func, callback)
        return func
    return wrapper


def respond_to(pattern, always=False, priority=30):
    '''
    Respond only to direct messages to the bot/mentions and not general
    listening.  It does this by using the mentions_self() method on the
    message object as a matcher condition.
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

        def preprocessor(message):
            mention_name = autobot.substitutions['mention_name']
            if message.startswith(mention_name):
                message = message[len(mention_name):].strip()
            return message

        matcher = autobot.Matcher(
                func,
                pattern,
                priority=priority,
                condition=condition,
                preprocessor=preprocessor
                )
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
        callback = autobot.EventCallback(func, event)
        _add_callback(func, callback)
        return func
    return wrapper


def _pattern_handler(matcher):
    _add_callback(matcher._func, matcher)
    LOG.debug('Adding pattern: %s as a matcher', matcher.pattern)


def _add_callback(func, callback):
    if not hasattr(func, '_callback_objects'):
        func._callback_objects = []
    func._callback_objects.append(callback)


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
        cron = croniter.croniter(cron_str, start_time=datetime.now())
        callback = autobot.ScheduledCallback(func, cron)
        _add_callback(func, callback)
        return func
    return wrapper
