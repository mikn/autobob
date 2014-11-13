import threading
from autobot import scheduler
from behave import *  # NOQA
from hamcrest import *  # NOQA


@given('I set the scheduler resolution to "{resolution}"')
def resolution(context, resolution):
    context.resolution = resolution


@when('The scheduler is started')
def start_scheduler(context):
    factory = {}
    scheduler_thread = threading.Thread(name='scheduler',
                                        target=scheduler.timer_thread,
                                        args=(factory, context.resolution)
                                        )
    context.scheduler = scheduler_thread


@then('I expect that the loops per second is "{fps}"')
def fps(context, fps):
    pass
