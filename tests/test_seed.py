import os
import warnings
from os.path import join as pjoin

import pytest

import jericho


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))
ROM = pjoin(DATA_PATH, "905.z5")
ROM_NO_BINDINGS = pjoin(DATA_PATH, "tw-game.z8")


def _rng_state(env):
    """ The emulator's RNG registers (the same ones get_state() captures). """
    lib = env.frotz_lib
    return (lib.getRngA(), lib.getRngInterval(), lib.getRngCounter())


def _quiet_env(*args, **kwargs):
    """ Builds an env, ignoring the transitional implicit-seed warning. """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", jericho.ImplicitRandomSeedWarning)
        return jericho.FrotzEnv(*args, **kwargs)


def test_default_seed_is_stochastic():
    # By default, the walkthrough seed should *not* be used silently.
    env = _quiet_env(ROM)
    assert env._seed == -1
    assert env.seed() == -1


def test_explicit_seed():
    env = jericho.FrotzEnv(ROM, seed=42)
    assert env._seed == 42

    # Zero is a valid seed.
    assert env.seed(0) == 0
    assert env._seed == 0


def test_seed_validation():
    env = jericho.FrotzEnv(ROM, seed=42)

    # The emulator takes a C int; values that don't fit must not silently wrap.
    # E.g. 2**32-1 would wrap to the -1 "stochastic" sentinel, silently
    # making an explicitly seeded env stochastic.
    for bad in (2**32 - 1, 2**31, -2**31 - 1):
        with pytest.raises(ValueError):
            env.seed(bad)
        with pytest.raises(ValueError):
            jericho.FrotzEnv(ROM, seed=bad)

    with pytest.raises(TypeError):
        env.seed(1.5)

    assert env.seed(2**31 - 1) == 2**31 - 1
    assert env.seed(-2**31) == -2**31


def test_walkthrough_seed_property():
    env = _quiet_env(ROM)
    assert env.walkthrough_seed == env.bindings['seed']

    # Games without bindings have no walkthrough seed.
    env = jericho.FrotzEnv(ROM_NO_BINDINGS)
    assert env.walkthrough_seed is None


def test_constructor_episode_uses_explicit_seed():
    # The episode set up at load time (playable without reset()) must honor
    # the constructor seed.
    rng1 = _rng_state(jericho.FrotzEnv(ROM, seed=1234))
    rng2 = _rng_state(jericho.FrotzEnv(ROM, seed=1234))
    rng3 = _rng_state(jericho.FrotzEnv(ROM, seed=4321))
    assert rng1 == rng2
    assert rng1 != rng3


def test_constructor_episode_is_stochastic():
    # ...and without a seed it must not fall back to the walkthrough seed.
    # Creating both envs within the same second is deliberate: seeds must come
    # from OS entropy rather than a clock, so that e.g. parallel workers
    # spawned together still play distinct episodes.
    env1 = _quiet_env(ROM)
    env2 = _quiet_env(ROM)
    assert _rng_state(env1) != _rng_state(env2)
    assert env1.episode_seed != env2.episode_seed


def test_unseeded_resets_are_stochastic():
    env = _quiet_env(ROM)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", jericho.ImplicitRandomSeedWarning)
        env.reset()
        rng1 = _rng_state(env)
        env.reset()  # A reset within the same second must still differ.
    assert _rng_state(env) != rng1


def test_episode_seed_reproduces_stochastic_episode():
    env = _quiet_env(ROM)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", jericho.ImplicitRandomSeedWarning)
        obs, info = env.reset()

    # The drawn seed is surfaced both as a property and in the info dict...
    assert info['seed'] == env.episode_seed

    # ...and replaying with it reproduces the episode exactly.
    replay = jericho.FrotzEnv(ROM, seed=env.episode_seed)
    assert _rng_state(replay) == _rng_state(env)

    # An explicitly seeded env reports its seed too.
    env = jericho.FrotzEnv(ROM, seed=42)
    assert env.episode_seed == 42
    obs, info = env.reset()
    assert info['seed'] == 42

    # A walkthrough-seeded episode reports the walkthrough seed.
    env = jericho.FrotzEnv(ROM)
    obs, info = env.reset(use_walkthrough_seed=True)
    assert info['seed'] == env.walkthrough_seed == env.episode_seed


def test_warning_when_using_implicit_random_seed():
    # Constructing is silent; the warning fires when the first episode is
    # actually played without an explicit seeding choice...
    env = jericho.FrotzEnv(ROM)
    with pytest.warns(jericho.ImplicitRandomSeedWarning):
        env.reset()

    # ...and only once per environment.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        env.reset()

    # The env is playable without reset(), so a bare step() must warn too.
    env = jericho.FrotzEnv(ROM)
    with pytest.warns(jericho.ImplicitRandomSeedWarning):
        env.step('look')

    # No warning when the choice is explicit.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        jericho.FrotzEnv(ROM, seed=-1).reset()
        jericho.FrotzEnv(ROM, seed=0).reset()
        jericho.FrotzEnv(ROM).reset(use_walkthrough_seed=True)

        env = jericho.FrotzEnv(ROM)
        env.seed()  # Deliberate request for stochastic episodes.
        env.reset()

    # No warning for games without a walkthrough seed.
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        jericho.FrotzEnv(ROM_NO_BINDINGS).reset()


def test_copy_preserves_seed_bookkeeping():
    env = _quiet_env(ROM)
    fork = env.copy()

    # The fork replays the parent's episode faithfully...
    assert _rng_state(fork) == _rng_state(env)
    assert fork.episode_seed == env.episode_seed
    # ...and keeps the parent's seed bookkeeping instead of silently becoming
    # "explicitly seeded" via the seed= constructor argument copy() uses.
    assert fork._seed_is_explicit == env._seed_is_explicit
    assert fork._warned_implicit_seed == env._warned_implicit_seed
    assert fork._episode_seed_implicit == env._episode_seed_implicit

    # A fork of an implicitly seeded env warns on its first episode, like the parent.
    with pytest.warns(jericho.ImplicitRandomSeedWarning):
        fork.step('look')

    fork = jericho.FrotzEnv(ROM, seed=42).copy()
    assert fork._seed_is_explicit


def test_reset_with_walkthrough_seed_but_no_bindings():
    # The caller asked for a specific deterministic setup that cannot be
    # honored; silently substituting another seed would be the same trap as
    # silently applying one (#84), so this must raise instead.
    env = jericho.FrotzEnv(ROM_NO_BINDINGS, seed=42)
    env.reset()
    rng1 = _rng_state(env)
    with pytest.raises(ValueError, match="walkthrough seed"):
        env.reset(use_walkthrough_seed=True)
    # The failed reset must not have touched the current episode.
    assert _rng_state(env) == rng1
    env.step('look')  # Still playable.


def test_reset_with_walkthrough_seed_applies_the_walkthrough_seed():
    # Cross-validate the flag against an env explicitly seeded with the
    # walkthrough seed. Score-based checks or back-to-back seeded resets can't
    # catch a broken flag: 905's walkthrough is RNG-independent, and two
    # time-based seeds drawn within the same second are identical anyway.
    env = jericho.FrotzEnv(ROM)
    walkthrough = env.get_walkthrough()
    prefix = walkthrough[:5]

    env.reset(use_walkthrough_seed=True)
    for act in prefix:
        env.step(act)

    ref = _quiet_env(ROM, seed=env.walkthrough_seed)
    ref.reset()
    for act in prefix:
        ref.step(act)

    assert _rng_state(env) == _rng_state(ref)
    assert env.get_world_state_hash() == ref.get_world_state_hash()


def test_walkthrough_is_reproducible_with_walkthrough_seed():
    env = jericho.FrotzEnv(ROM)
    walkthrough = env.get_walkthrough()

    env.reset(use_walkthrough_seed=True)
    for act in walkthrough:
        obs, rew, done, info = env.step(act)

    assert done
    assert info["score"] == env.get_max_score()


def test_set_state_restores_rng_across_envs():
    # get_valid_actions(use_parallel=True) forks worker envs which sync via
    # set_state(); this is only sound if set_state restores the RNG registers,
    # since the workers no longer share the parent's (walkthrough) seed.
    env = _quiet_env(ROM)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", jericho.ImplicitRandomSeedWarning)
        env.reset()
        for act in env.get_walkthrough()[:3]:
            env.step(act)
    state = env.get_state()

    worker = jericho.FrotzEnv(ROM, seed=-1)  # Different randomly drawn seed.
    worker.set_state(state)
    assert _rng_state(worker) == _rng_state(env)
