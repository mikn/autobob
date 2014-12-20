from behave import *  # NOQA
from hamcrest import *  # NOQA

import time
import threading
import autobot


@given('I set the scheduler resolution to {resolution}')
def resolution(context, resolution):
    context.resolution = resolution


@when('The scheduler is started')
def start_scheduler(context):
    factory = {}
    scheduler_thread = threading.Thread(name='scheduler',
                                        target=autobot.scheduler.timer_thread,
                                        args=(factory, context.resolution)
                                        )
    context.scheduler = scheduler_thread


@then('Thread is running')
def running_thread(context):
    assert_that(context.scheduler.is_alive)


@then('I expect that the loops per second is {fps}')
def fps(context, fps):
    begin = time.monotonic()
    for i in range(0, 10):
        pass
    thread_fps = time.monotonic() - begin
    assert_that(fps, close_to(thread_fps))


@given('I have a scheduler')
def generic(context):
    context.resolution = 0.5
