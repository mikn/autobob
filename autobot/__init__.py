import logging
import sys

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(format))
error_handler.setLevel(logging.ERROR)
LOG.addHandler(error_handler)

# The order here is important...
# We start with stateless objects that have few to no internal dependencies
from .objects import *  # NOQA

# Global lists
from .event import Events  # NOQA
event = Events()

from .substitutions import Substitutions  # NOQA
substitutions = Substitutions()

# Then we move on to the factory
from .factory import Factory  # NOQA

# Most of the rest of the application depend on the factory being present
from . import core  # NOQA
from . import scheduler  # NOQA
from . import brain  # NOQA
from .decorators import *  # NOQA

# CONSTANTS
PRIORITY_ALWAYS = -1
SELF_MENTION = 'SELF_MENTION'
