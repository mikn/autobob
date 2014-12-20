import os.path
import sys
import threading
import logging
import toml

LOG = logging.getLogger(__name__)

import autobot
import autobot.config
from . import brain
from . import scheduler

# TODO: Core Admin Plugin
# TODO: Read an ACTUAL configuration file
# TODO: Plugin folder scaffolding script
# TODO: Live plugin reloads using inotify
# TODO: XMPP Plugin
# TODO: HipChat Plugin
# TODO: Testing using Behave
# TODO: Documentation using Sphinx
# TODO: Format {} shorthands in plugins
# TODO: Redis Plugin
# TODO: ACL..?
# TODO: Nicer CLI than logger?
# TODO: Share lock for all methods on same object (difficult without
# performance impact)


def main():
    logging.getLogger('autobot').setLevel(logging.DEBUG)

    f = ''

    config = autobot.config.defaults
    if f and os.path.exists(f):
        LOG.debug('Reading configuration file from {}!'.format(f))
        with open(f) as conf:
            config.update(toml.loads(conf))

    LOG.debug('Importing plugins!')
    factory = autobot.plugins.Factory(config)

    brain_thread = threading.Thread(
        name='brain',
        target=brain.boot,
        args=(factory,)
    )

    timer_thread = threading.Thread(
        name='timer',
        target=scheduler.timer_thread,
        args=(factory, config.get('scheduler_resolution'))
    )

    LOG.debug('Booting brain!')
    try:
        brain_thread.start()

        LOG.debug('Revving up the scheduler!')
        timer_thread.start()

        LOG.debug('Starting service listener!')
        service = factory.get_service()
        service.run()

        [m.compile(mention_name=service.mention_name) for m in brain.matchers]

        # Make sure the main thread is blocking so we can catch the interrupt
        brain_thread.join()
        timer_thread.join()

    except (KeyboardInterrupt, SystemExit):
        LOG.info('\nI have been asked to quit nicely, and so I will!')
        brain.shutdown()
        scheduler.shutdown()
        sys.exit()


if __name__ == '__main__':
    main()
