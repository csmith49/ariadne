import time
import logging

# the logger by which theseus emits messages
log = logging.getLogger(__name__)

# default initialization for log
log.addHandler(logging.NullHandler())

# base message formats
OPEN_MSG = "OPEN|%(region)s"
CLOSE_MSG = "CLOSE|%(region)s"
INIT_MSG = "INIT"
VALUE_MSG = "VALUE|%(id)s|%(value)s"

# value representation
class Value:
    def __init__(self, value):
        self.value = value
    def __str__(self):
        if isinstance(self.value, bool):
            return f"{{BOOL:{self.value}}}"
        elif isinstance(self.value, int):
            return f"{{INT:{self.value}}}"
        else:
            return f"{{STRING:{self.value}}}"    

# minimal annotations
def tag(id, value):
    log.debug(VALUE_MSG, {"id": id, "value": Value(value)})
    return value

class ContextWrapper:
    def __init__(self, region):
        self.region = region
    def __enter__(self):
        log.debug(OPEN_MSG, {"region": self.region})
    def __exit__(self, *args, **kwargs):
        log.debug(CLOSE_MSG, {"region": self.region})
    def __call__(self, func):
        def wrapped(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
                return tag("result", result)
        return wrapped

def context(region):
    return ContextWrapper(region)

# initialization - without this, nothing really happens
def initialize(target):
    logging.basicConfig(level=logging.DEBUG)
    # simply, we write out to target file
    handler = logging.FileHandler(target)
    # formatter = logging.Formatter(datefmt="%(created)f")
    # the handler uses a simplified formatter
    # handler.setFormatter(formatter)
    log.addHandler(handler)
    log.debug(INIT_MSG)