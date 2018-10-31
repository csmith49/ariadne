import theseus

theseus.initialize("thread.log")

with theseus.context("loop"):
    for i in range(1, 10):
        with theseus.context("body"):
            theseus.tag("counter", i)
        with theseus.context("body2"):
            print(i)