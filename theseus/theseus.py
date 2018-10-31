import time
import logging

# message formats - taken from THREAD documentation
OPEN_MESSAGE = "OPEN|%(region)s"
CLOSE_MESSAGE = "CLOSE|%(region)s"
INIT_MESSAGE = "INIT"
TERMINATE_MESSAGE = "TERMINATE"
VALUE_MESSAGE = "VALUE|%(id)s|%(value)s"

# our log level is just above info
LOG_LEVEL = 21

# wrapper for formatting values - rep taken from THREAD documentation
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

# context wrappers ensure open and closed called appropriately
class ContextWrapper:
    def __init__(self, region, thread):
        self.region = region
        self.thread = thread
    def __enter__(self):
        self.thread.open(self.region)
    def __exit__(self, *args, **kwargs):
        self.thread.close(self.region)
    # enables decorator usage
    def __call__(self, func):
        def wrapped(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
                return self.thread.tag("result", result)
        return wrapped

# primary means of interface is with Thread objects
class Thread:
    # threads require an entity to be named - safe bet is the name of the file
    def __init__(self, entity, level=LOG_LEVEL):
        self.entity = entity
        self.level = level
        self._log = logging.getLogger(entity)
        self._formatter = logging.Formatter(f"THREAD|{entity}|%(relativeCreated)d|%(message)s")
        # make sure log has a handler by default
        self._log.addHandler(logging.NullHandler())
    
    # the basic interface
    def open(self, region):
        self._log.log(self.level, OPEN_MESSAGE, {"region": region})
    def close(self, region):
        self._log.log(self.level, CLOSE_MESSAGE, {"region": region})
    def tag(self, id, value):
        self._log.log(self.level, VALUE_MESSAGE, {"id": id, "value": Value(value)})
    def context(self, region):
        return ContextWrapper(region, self)

    # termination takes no arguments
    def terminate(self):
        self._log.log(self.level, TERMINATE_MESSAGE)
    
    # initialization configures the logger destination - currently only handles files
    def initialize(self, target):
        # construct a handler for all messages emitted from this thread
        handler = logging.FileHandler(target)
        handler.setFormatter(self._formatter)
        handler.setLevel(self.level)

        # configure the log to use the appropriate handler
        self._log.addHandler(handler)
        self._log.setLevel(self.level)

        # and finally emit the init message
        self._log.log(self.level, INIT_MESSAGE)