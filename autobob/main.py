import os.path
import sys
import threading
import logging
import toml

LOG = logging.getLogger(__name__)

import autobob
from . import brain
from . import plugins
from . import config

# TODO: Read an ACTUAL configuration file
# TODO: Scheduler
# TODO: XMPP Plugin
# TODO: HipChat Plugin
# TODO: Plugin folder scaffolding script
# TODO: Documentation
# TODO: Redis Plugin
# TODO: Format {} shorthands in plugins
# TODO: Core Admin Plugin
# TODO: ACL..?
# TODO: Nicer CLI than logger?
# TODO: Share lock for all methods on same object (difficult without
# performance impact)


def main():
    logging.getLogger('autobob').setLevel(logging.DEBUG)

    f = ''

    config = autobob.config.defaults
    if f and os.path.exists(f):
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

        [m.compile(mention_name=service.mention_name) for m in brain.matchers]

        # Make sure the main thread is blocking so we can catch the interrupt
        brain_thread.join()

    except (KeyboardInterrupt, SystemExit):
        LOG.info('\nI have been asked to quit nicely, and so I will!')
        autobob.brain.shutdown()
        sys.exit()


if __name__ == '__main__':
    main()
