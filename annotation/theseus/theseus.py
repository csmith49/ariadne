import time

# by default, the entity name is THESEUS
ENTITY = "THESEUS"

# utility functions
# current utc time in milliseconds
def current_time(): return int(round(time.time() * 1000))

# message generation functions
def encode_value(value):
    if isinstance(value, bool):
        return f"{{BOOL:{value}}}"
    elif isinstance(value, int):
        return f"{{INT:{value}}}"
    else:
        return f"{{STRING:{value}}}"

def front_matter(): return f"THREAD|{ENTITY}|{current_time()}"

def init_message(): return f"{front_matter()}|INIT"

def value_message(id, value): 
    return f"{front_matter()}|VALUE|{id}|{encode_value(value)}"

def open_message(region):
    return f"{front_matter()}|OPEN|{region}"

def close_message(region):
    return f"{front_matter()}|CLOSE|{region}"

# context
def tag(id, value):
    print(value_message(id, value))
    return value

class ContextWrapper:
    def __init__(self, region):
        self.region = region
    def __enter__(self):
        print(open_message(self.region))
    def __exit__(self, *args, **kwargs):
        print(close_message(self.region))
    def __call__(self, func):
        def wrapped(*args, **kwargs):
            with self:
                result = func(*args, **kwargs)
                return tag("result", result)
        return wrapped

def context(region):
    return ContextWrapper(region)

# the very last thing we do after importing is send the init message
print(init_message())