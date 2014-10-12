import time
import threading
import logging
LOG = logging.getLogger(__name__)

import autobob.brain
import autobob.plugins

# TODO: Factory and bindings between Client and main loop
# TODO: Make the main loop agnostic of different types of matchers
# TODO: Testing
# TODO: XMPP Plugin
# TODO: Redis Plugin
# TODO: HipChat Plugin
# TODO: Configuration
# TODO: Scheduler
# TODO: Allow bot to reply with more than one handler?


def main():
    logging.getLogger('autobob').setLevel(logging.DEBUG)

    LOG.debug('Importing plugins!')
    factory = autobob.plugins.Factory()

    brain_thread = threading.Thread(
        name='brain',
        target=autobob.brain.boot,
        args=(factory,)
    )
    LOG.debug('Booting brain!')
    brain_thread.start()

    LOG.debug('Starting Service Listener!')
    fakemsg = autobob.robot.Message('Hello botname!', 'athur!')
    autobob.brain.messageq.put(fakemsg)
    time.sleep(2)
    autobob.brain.messageq.put(fakemsg)
    time.sleep(2)
    autobob.brain.messageq.put(fakemsg)


if __name__ == '__main__':
    main()
