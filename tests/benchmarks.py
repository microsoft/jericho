import os
import time
from os.path import join as pjoin

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


def bench_loading_speed():
    REPEAT = 1000

    start = time.time()
    rom = pjoin(DATA_PATH, "905.z5")
    for _ in range(REPEAT):
        env = jericho.FrotzEnv(rom)
        env.reset()
        env.close()

    duration1 = time.time() - start
    print("Calling FrotzEnv({}) {} times in {:6.2f} secs.".format(rom, REPEAT, duration1))
    del env

    start = time.time()
    env = jericho.FrotzEnv(rom)
    for _ in range(REPEAT - 1):
        env.load(rom)
        env.reset()
        env.close()

    duration2 = time.time() - start
    print("Calling env.load({}) {} times in {:6.2f} secs.".format(rom, REPEAT, duration2))
    print("Speedup: {}x.".format(duration1 / duration2))


if __name__ == "__main__":
    bench_loading_speed()
