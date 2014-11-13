import bisect
import math
import logging
import queue
import time

LOG = logging.getLogger(__name__)

scheduleq = queue.Queue()


def timer_thread(factory, resolution):
    scheduled_events = []
    LOG.debug('Setting loops per second to: %.2f', 1 / resolution)
    while True:
        bt = time.monotonic()
        unix_time = time.time()
        _process_event(factory, scheduled_events, unix_time, resolution)
        try:
            event = scheduleq.get_nowait()
            if not event:
                scheduleq.task_done()
                break
            _schedule_event(event, scheduled_events)
            scheduleq.task_done()
        except queue.Empty:
            pass
        time_spent = time.monotonic() - bt
        # Make the loop tick on .0 unix time for style points
        sleep_time = resolution - math.fmod(unix_time + time_spent, resolution)
        if sleep_time < 0:
            sleep_time = 0
        time.sleep(sleep_time)


def shutdown():
    scheduleq.put(False)


def _process_event(factory, scheduled_events, unix_time, resolution):
    '''
    This is a separate method, mainly because I did not want to wrap the entire
    block in an if-statement if the scheduled_events would be empty.
    '''
    if not scheduled_events:
        return True
    exec_time = scheduled_events[0].timestamp
    if unix_time >= exec_time:
        event = scheduled_events.pop(0)
        LOG.debug('Running scheduled event %s at: %d', event, unix_time)
        callback = event.get_callback(factory)
        callback()
        event.get_next()
        _schedule_event(event, scheduled_events)


def _schedule_event(event, scheduled_events):
    LOG.debug('Scheduling event %s to happen at: %d', event, event.timestamp)
    loc = bisect.bisect_left(scheduled_events, event)
    scheduled_events.insert(loc, event)
