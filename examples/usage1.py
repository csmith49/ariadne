import theseus
import time

thread = theseus.Thread("usage1")
thread.initialize("thread.log")

with thread.context("loop"):
    for i in range(1, 10):
        with thread.context("body"):
            thread.tag("counter", i)
        with thread.context("body2"):
            print(i)

thread.terminate()
