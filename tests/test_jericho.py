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


def test_saving_opcode_in_state():
    # At some point in yomomma.z8, the player is asked to hit [enter] to continue.
    # Restoring to that particular state without setting the opcode appropriately
    # would result in the emulated halting.
    COMMANDS = [
        'south', 'southeast', 'sit', 'wait', 'yes', 'west', 'north',  # Actions needed to reach the corner case.
        'get in stage',  # -> opcode == 246 (z_read_char)
        '',  # Pressing [enter] -> opcode == 246 (z_read_char)
        '[save]',
        '',  # Pressing [enter] -> opcode == 228 (z_read_line)
        '[restore]',  # If not resetted properly, opcode == 228 (z_read_line) instaead of 246 (z_read_char)
        'examine something',  # Causes an illegal opcode
        'look'  # Emulator has halted.
    ]

    rom = pjoin(DATA_PATH, "roms", "yomomma.z8")
    if not os.path.exists(rom):
        raise unittest.SkipTest("Missing data: {}".format(rom))

    env = jericho.FrotzEnv(rom)
    env.reset()

    state = None
    for cmd in COMMANDS:
        if cmd == "[save]":
            state = env.get_state()
        elif cmd == "[restore]":
            env.set_state(state)
        else:
            obs, rew, done, info = env.step(cmd)
            assert not env._emulator_halted()


def test_very_long_action():
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom)
    env.reset()

    long_command = "It's a " + "very " * 36 + "long action!"
    assert len(long_command) == 199
    env.step(long_command)
    env.step(long_command * 2)

    long_command = "It's a " + "très " * 36 + "long action!"
    assert len(long_command) == 199
    env.step(long_command)
    env.step(long_command * 2)
