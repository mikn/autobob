import functools

import autobob.brain
import autobob.robot


def always(func):
    autobob.brain.catchalls.append(func)
    return func


# Important to remember that the funcs here are CLASS methods
# Should probably get the class from the factory before passing it into
# the matcher object
def respond_to(func, pattern):
    matcher = autobob.robot.Matcher(func, pattern)
    autobob.brain.mention_matchers.append(matcher)
    return func


def hear(func, pattern):
    matcher = autobob.robot.Matcher(func, pattern)
    autobob.brain.matchers.append(matcher)
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
