import time
import queue
import logging

LOG = logging.getLogger(__name__)


scheduleq = queue.Queue()
events = []


def timer_thread():
    while True:
        try:
            event = scheduleq.get_nowait()
            if not event:
                break
            events.append(event.timestamp, event)
            events.sort()
        except queue.Empty:
            pass

        rounded_time = int(time.time())
        if events:
            while events[0][0] <= rounded_time:
                timestamp, callback = events.pop(0)
                if timestamp < rounded_time:
                    LOG.info('We did not have time to run {} as scheduled. '
                             'Running it {} seconds late.'
                             ''.format(callback, rounded_time - timestamp))
                callback.get_callback()()
                callback.get_next()
                scheduleq.put(callback)

        time.sleep(1)


def shutdown():
    LOG.debug('Shutting down scheduler...')
    scheduleq.put(False)
