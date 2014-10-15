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

# TODO: Testing
# TODO: Shelve Plugin
# TODO: XMPP Plugin
# TODO: HipChat Plugin
# TODO: Redis Plugin
# TODO: Scheduler
# TODO: Plugin folder scaffolding script
# TODO: Allow bot to reply with more than one handler?


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
    brain_thread.start()

    LOG.debug('Starting Service Listener!')
    service = factory.get_service()
    service.run()


if __name__ == '__main__':
    main()
