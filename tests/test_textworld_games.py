import os
from os.path import join as pjoin

import jericho


TEST_GAME = os.path.abspath(pjoin(__file__, '..', "tw-game.z8"))


def test_loading_a_textworld_game():
    env = jericho.FrotzEnv(TEST_GAME)
    state = env.reset()

    assert not env.victory()
    assert not env.game_over()
    assert env.get_score() == 0
    assert env.get_max_score() == 3

    state, score, done, _ = env.step("go east")
    assert not done
    assert score == 0

    state, score, done, _ = env.step("insert carrot into chest")
    assert not done
    assert score == 2

    state, score, done, _ = env.step("close chest")
    assert done
    assert env.victory()
    assert score == 3

    state = env.reset()
    state, score, done, _ = env.step("eat carrot")
    assert done
    assert env.game_over()  # Lost
    assert score == 0
