import sys
import logging

LOG = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
LOG.addHandler(handler)
error_handler = logging.StreamHandler(sys.stderr)
error_handler.setFormatter(logging.Formatter(format))
error_handler.setLevel(logging.ERROR)
LOG.addHandler(error_handler)

from .robot import Service, Storage
from .decorators import *
