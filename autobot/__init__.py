import logging
import sys

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(format))
error_handler.setLevel(logging.ERROR)
LOG.addHandler(error_handler)

from .objects import *  # NOQA
from .factory import Factory  # NOQA
from . import core  # NOQA
from . import scheduler  # NOQA
from .decorators import *  # NOQA
from . import event  # NOQA

# CONSTANTS
PRIORITY_ALWAYS = -1
SELF_MENTION = 'SELF_MENTION'
