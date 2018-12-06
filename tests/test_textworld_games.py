import os
from os.path import join as pjoin

import jericho


TEST_GAME = os.path.abspath(pjoin(__file__, '..', "tw-game.z8"))
TEST_GAME2 = os.path.abspath(pjoin(__file__, '..', "tw-game-very-long-filename-but-not-that-long-though.z8"))



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


def test_loading_several_textworld_games():
    for i in range(10):
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
        env.close()


def test_loading_several_textworld_games2():
    for i in range(10):
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
        env.close()

        env = jericho.FrotzEnv(TEST_GAME2)
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
        env.close()

