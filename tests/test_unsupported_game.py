import os
import warnings
from os.path import join as pjoin

import jericho
from jericho import UnsupportedGameWarning

# Note: dummy.z8 is the same as tw-game.z8.
TEST_GAME = os.path.abspath(pjoin(__file__, '..', "dummy.z8"))


def test_loading_unsupported_game():
    with warnings.catch_warnings(record=True) as w:
        env = jericho.FrotzEnv(TEST_GAME)
        warnings.simplefilter("always")
        assert len(w) == 1
        assert issubclass(w[-1].category, UnsupportedGameWarning)
        assert TEST_GAME in str(w[-1].message)

    state = env.reset()
    assert env.get_score() == 0
    assert env.get_max_score() == 0  # Instead of 3.

    state, score, done, _ = env.step("go east")
    state, score, done, _ = env.step("insert carrot into chest")
    assert score == 0  # Instead of 2.
    state, score, done, _ = env.step("close chest")
    assert score == 0  # Instead of 3.

    assert "The End" in state
    assert not done  # Instead of True
    assert not env.victory()  # Instead of True

    state = env.reset()
    state, score, done, _ = env.step("eat carrot")
    assert "You lost" in state
    assert not done  # Instead of True
    assert not env.game_over()  # Instead of True
