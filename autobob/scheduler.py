import asyncio
import logging
import queue
import time

LOG = logging.getLogger(__name__)

scheduleq = queue.Queue()


def timer_thread(factory):
    loop = asyncio.new_event_loop()
    loop.call_later(1, check_queue, loop, factory)
    loop.run_forever()
    loop.close()


def shutdown():
    LOG.debug('Shutting down scheduler...')
    scheduleq.put(False)


# TODO: Move this logic to a coroutine instead perhaps?
def check_queue(loop, factory):
    try:
        event = scheduleq.get_nowait()
        if not event:
            loop.stop()
            scheduleq.task_done()
            return
        schedule(loop, event, factory)
        scheduleq.task_done()
    except queue.Empty:
        pass

    loop.call_later(1, check_queue, loop, factory)


def schedule(loop, event, factory):
    unixtime = time.time()
    diff = event.timestamp - unixtime
    call_at = loop.time() + diff
    LOG.debug('Adding callback with timestamp: {}'.format(int(event.timestamp)))
    LOG.debug('T minus {} seconds.'.format(round(diff)))
    loop.call_at(call_at, event_callback, loop, event, factory)


def event_callback(loop, event, factory):
    LOG.debug('Calling callback with timestamp: {}'.format(int(event.timestamp)))
    event.get_callback(factory)()
    event.get_next()
    schedule(loop, event, factory)
