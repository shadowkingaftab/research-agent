import time


class Profiler:

    def __init__(self):
        self.times = {}

    def start(self, name):
        self.times[name] = time.perf_counter()

    def stop(self, name):

        elapsed = time.perf_counter() - self.times[name]

        print(f"{name}: {elapsed:.2f}s")

        return elapsed


profiler = Profiler()