import bisect
import math
import logging
import queue
import time
import threading
from . import workers

LOG = logging.getLogger(__name__)

scheduleq = queue.Queue()
thread_pool = []


def timer_thread(factory, resolution):
    '''
    The basic function of the timer loop is that it receives events to schedule
    and if there are events to schedule, it will schedule them. If there are
    events up for execution, it will execute them and then add another event
    to schedule to the schedule queue.
    Since it works this way, we can make it speedy if there is a need, for
    instance if there's a lot of events that happen at the same time, but we
    can also loop with larger sleeps when there's nothing to do.
    It dispatches the callback execution to a thread pool which then deals
    with the execution. This thread pool is proportionate in size to the
    number of cores available.
    '''
    global thread_pool
    scheduled_events = []
    thread_pool = workers.init_threads(workers.schedule_worker, ())
    LOG.debug('Setting loops per second to: %.2f', 1 / resolution)
    while True:
        begin_time = time.monotonic()
        unix_time = time.time()
        _process_event(factory, scheduled_events, unix_time, resolution)
        quit = _process_queue(scheduled_events)
        if quit:
            break

        time_spent = time.monotonic() - begin_time
        # Make the loop tick on .0 unix time for style points
        sleep_time = resolution - math.fmod(unix_time + time_spent, resolution)
        # We don't need to sleep if we have a queue or spent too much time
        if sleep_time < 0 or scheduleq.qsize() > 0:
            sleep_time = 0
        time.sleep(sleep_time)


def shutdown():
    workers.shutdown_pool(thread_pool, workers.callbackq)
    scheduleq.put(False)
    scheduleq.join()


def _process_queue(scheduled_events):
    quit = False
    try:
        while True:
            event = scheduleq.get_nowait()
            if not event:
                scheduleq.task_done()
                quit = True
                break
            _schedule_event(event, scheduled_events)
            scheduleq.task_done()
    except queue.Empty:
        pass
    return quit


def _process_event(factory, scheduled_events, unix_time, resolution):
    '''
    This is a separate method, mainly because I did not want to wrap the entire
    block in an if-statement if the scheduled_events would be empty.
    '''
    if not scheduled_events:
        return False
    exec_time = scheduled_events[0].timestamp
    event_thread = None
    if unix_time >= exec_time:
        event = scheduled_events.pop(0)
        LOG.debug('Running scheduled event %s at: %d', event, unix_time)
        callback = event.get_callback(factory)
        event_thread = threading.Thread(target=callback)
        event_thread.run()
        event.get_next()
        _schedule_event(event, scheduled_events)
    return event_thread


def _schedule_event(event, scheduled_events):
    LOG.debug('Scheduling event %s to happen at: %d', event, event.timestamp)
    loc = bisect.bisect_left(scheduled_events, event)
    scheduled_events.insert(loc, event)
