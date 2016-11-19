import os
import sys
import threading
import logging
import toml
import argparse
import queue

import autobot
import autobot.config

LOG = logging.getLogger(__name__)

# TODO: Output formatter system
# TODO: Make dev help and normal help output different things
# TODO: HipChat Plugin
# TODO: Core Admin Plugin
# TODO: Plugin folder scaffolding script
# TODO: Live plugin reloads using inotify
# TODO: Testing using Behave
# TODO: Create fake factory that satisfies the needs of the brain thread
# TODO: Documentation using Sphinx
# TODO: Redis Plugin
# TODO: ACL..?
# TODO: Nicer CLI than logger?


def parse_args():
    parser = argparse.ArgumentParser(
        description='The primary foreground script for the chatbot library '
        'autobot')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug output')
    parser.add_argument('--config-file', help='The configuration file')
    parser.add_argument('--custom-plugins', help='The folder in which '
                        'to look for custom plugins to execute with.',
                        default=os.curdir)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.debug:
        logging.getLogger('autobot').setLevel(logging.DEBUG)

    f = args.config_file

    config = autobot.config.defaults
    if f and os.path.exists(f):
        LOG.debug('Reading configuration file from %s!', f)
        with open(f) as conf:
            config.update(toml.loads(conf.read()))

    matchers = []
    catchalls = []
    event_callbacks = autobot.event
    workq = queue.Queue()
    messageq = queue.Queue()
    scheduleq = queue.Queue()
    mapping = {
            autobot.Callback: catchalls.append,
            autobot.Matcher: matchers.append,
            autobot.ScheduledCallback: scheduleq.put,
            autobot.EventCallback: event_callbacks.add_handler,
    }

    factory = autobot.Factory(config, mapping)
    LOG.debug('Importing plugins!')
    factory.start()

    brain = autobot.brain.Brain(factory, matchers, catchalls, messageq, workq)
    brain_thread = threading.Thread(name='brain', target=brain.boot)

    scheduler = autobot.scheduler.Scheduler(
                factory, config.get('scheduler_resolution'), scheduleq, workq
                )
    scheduler_thread = threading.Thread(name='timer', target=scheduler.boot)

    worker_pool = autobot.workers.WorkerPool(workq)

    try:
        worker_pool.start()
        brain_thread.start()
        scheduler_thread.start()

        LOG.debug('Starting service listener!')
        service = factory.get_service()
        service.set_message_queue(messageq)
        service.start()

        # Make sure the main thread is blocking so we can catch the interrupt
        brain_thread.join()
        scheduler_thread.join()

    except (KeyboardInterrupt, SystemExit):
        LOG.info('\nI have been asked to quit nicely, and so I will!')
        scheduler.shutdown()
        service.shutdown()
        brain.shutdown()
        worker_pool.shutdown()
        sys.exit()


if __name__ == '__main__':
    main()
