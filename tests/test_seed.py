import os
import warnings
from os.path import join as pjoin

import pytest

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


def test_default_seed_is_time_dependent():
    # By default, the walkthrough seed should *not* be used silently.
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom)
    assert env._seed == -1
    assert env.seed() == -1


def test_explicit_seed():
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom, seed=42)
    assert env._seed == 42

    # Zero is a valid seed.
    assert env.seed(0) == 0
    assert env._seed == 0


def test_walkthrough_seed_property():
    env = jericho.FrotzEnv(pjoin(DATA_PATH, "905.z5"))
    assert env.walkthrough_seed == env.bindings['seed']

    # Games without bindings have no walkthrough seed.
    env = jericho.FrotzEnv(pjoin(DATA_PATH, "tw-game.z8"))
    assert env.walkthrough_seed is None


def test_warning_when_using_implicit_random_seed():
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom)

    with pytest.warns(jericho.ImplicitRandomSeedWarning):
        env.reset()

    # No warning when the choice is explicit.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        env.reset(use_walkthrough_seed=True)
        jericho.FrotzEnv(rom, seed=-1).reset()
        jericho.FrotzEnv(rom, seed=env.walkthrough_seed).reset()

    # No warning for games without a walkthrough seed.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        jericho.FrotzEnv(pjoin(DATA_PATH, "tw-game.z8")).reset()


def test_reset_with_walkthrough_seed_but_no_bindings():
    env = jericho.FrotzEnv(pjoin(DATA_PATH, "tw-game.z8"))
    with pytest.warns(jericho.UnsupportedGameWarning):
        env.reset(use_walkthrough_seed=True)


def test_walkthrough_is_reproducible_with_walkthrough_seed():
    rom = pjoin(DATA_PATH, "905.z5")
    env = jericho.FrotzEnv(rom)
    walkthrough = env.get_walkthrough()

    env.reset(use_walkthrough_seed=True)
    for act in walkthrough:
        obs, rew, done, info = env.step(act)

    assert done
    assert info["score"] == env.get_max_score()
