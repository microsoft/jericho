import os
import sys
import unittest
from os.path import join as pjoin

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


def test_multiple_instances():
    gamefile1 = pjoin(DATA_PATH, "905.z5")
    gamefile2 = pjoin(DATA_PATH, "tw-game.z8")

    # Make sure both frotz_lib have different handles.
    env1 = jericho.FrotzEnv(gamefile1)
    env2 = jericho.FrotzEnv(gamefile2)
    assert env1.frotz_lib._handle != env2.frotz_lib._handle

    # Test we can play two different games in parallel.
    state1, _ = env1.reset()
    state2, _ = env2.reset()
    assert "9:05 by Adam Cadre" in state1
    assert "TextWorld" in state2

    state1, _, _, _ = env1.step("examine me")
    env1.close()
    assert "You're covered with mud and dried sweat." in state1

    state2, _, _, _ = env2.step("examine me")
    env2.close()
    assert "As good-looking as ever." in state2


def test_for_memory_leaks():
    # Make sure we don't have severe memory leaks.

    def _get_mem():
        import resource
        return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

    unit = 1024  # Denominator to get memory usage in MB.
    if sys.platform == 'darwin':
        # According to https://github.com/apple/darwin-xnu/blob/master/bsd/man/man2/getrusage.2#L95
        # OSX outputs ru_maxrss in bytes rather then kilobytes.
        unit = 1024 * 1024

    gamefile1 = pjoin(DATA_PATH, "905.z5")
    env1 = jericho.FrotzEnv(gamefile1)
    env1.reset()
    del env1

    mem_start = _get_mem()
    print('Memory usage: {:.1f}MB'.format(mem_start / unit))
    for _ in range(1000):
        # Make sure we don't have memory leak.
        env1 = jericho.FrotzEnv(gamefile1)
        env1.reset()
        del env1

    mem_mid = _get_mem()
    print('Memory usage: {:.1f}MB ({:+.1f}MB)'.format(
           mem_mid / unit, (mem_mid-mem_start) / unit ))

    for _ in range(1000):
        env1 = jericho.FrotzEnv(gamefile1)
        env1.reset()
        del env1

    mem_end = _get_mem()
    print('Memory usage: {:.1f}MB ({:+.1f}MB)'.format(
          mem_end / unit, (mem_end-mem_mid) / unit))

    # Less than 1MB memory leak per 1000 load/unload cycles.
    assert (mem_mid - mem_start) < unit * unit
    assert (mem_end - mem_mid) < unit * unit


def test_copy():
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom)
    env.reset()

    walkthrough = env.get_walkthrough()
    expected = [env.step(act) for act in walkthrough]

    env.reset()
    for i, act in enumerate(walkthrough):
        obs, rew, done, info = env.step(act)

        if i + 1 < len(walkthrough):
            fork = env.copy()
            for j, cmd in enumerate(walkthrough[i+1:], start=i+1):
                obs, rew, done, info = fork.step(cmd)
                assert (obs, rew, done, info) == expected[j]
