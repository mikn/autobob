import sys
import signal
import time
import threading
import logging
import toml

LOG = logging.getLogger(__name__)

import autobob
import autobob.brain
import autobob.plugins
import autobob.config

# TODO: Catch exceptions in threads to prevent them from dying
# TODO: Parse for mentions through Service
# TODO: Share lock for all methods on same object (difficult without
# performance impact)
# TODO: XMPP Plugin
# TODO: HipChat Plugin
# TODO: Redis Plugin
# TODO: Scheduler
# TODO: Plugin folder scaffolding script


def main():
    logging.getLogger('autobob').setLevel(logging.DEBUG)

    f = ''

    config = autobob.config.defaults
    if f and exists(f):
        LOG.debug('Reading configuration file from {}!'.format(f))
        with open(f) as conf:
            config.update(toml.loads(conf))

    LOG.debug('Importing plugins!')
    factory = autobob.plugins.Factory(config)

    brain_thread = threading.Thread(
        name='brain',
        target=autobob.brain.boot,
        args=(factory,)
    )
    LOG.debug('Booting brain!')
    try:
        brain_thread.start()

        LOG.debug('Starting Service Listener!')
        service = factory.get_service()
        service.run()

        # Make sure the main thread is blocking so we can catch the interrupt
        # event
        brain_thread.join()

    except (KeyboardInterrupt, SystemExit):
        LOG.info('\nI have been asked to quit nicely, and so I will!')
        autobob.brain.shutdown()
        sys.exit()


if __name__ == '__main__':
    main()
