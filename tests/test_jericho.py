import os
import unittest
from os.path import join as pjoin

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


class TestJericho(unittest.TestCase):
    def test_load_bindings(self):
        self.assertRaises(ValueError, jericho.load_bindings, "")
        data1 = jericho.load_bindings("905")
        data2 = jericho.load_bindings("905.z5")
        assert data1 == data2

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

    gamefile1 = pjoin(DATA_PATH, "905.z5")
    env1 = jericho.FrotzEnv(gamefile1)
    env1.reset()
    del env1

    mem_start = _get_mem()
    print('Memory usage: {:.1f}MB'.format(mem_start / 1024))
    for _ in range(1000):
        # Make sure we don't have memory leak.
        env1 = jericho.FrotzEnv(gamefile1)
        env1.reset()
        del env1

    mem_mid = _get_mem()
    print('Memory usage: {:.1f}MB ({:+.1f}MB)'.format(
           mem_mid / 1024, (mem_mid-mem_start) / 1024 ))

    for _ in range(1000):
        env1 = jericho.FrotzEnv(gamefile1)
        env1.reset()
        del env1

    mem_end = _get_mem()
    print('Memory usage: {:.1f}MB ({:+.1f}MB)'.format(
          mem_end / 1024, (mem_end-mem_mid) / 1024))

    # Less than 1MB memory leak per 1000 load/unload cycles.
    assert (mem_mid - mem_start) < 1024*1024
    assert (mem_end - mem_mid) < 1024*1024
