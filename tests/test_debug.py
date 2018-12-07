# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT license.


import os
import pickle
import shutil
import tempfile
import unittest
import contextlib
from os.path import join as pjoin

import numpy as np
import numpy.testing as npt

import jericho


TEST_GAME = os.path.abspath(pjoin(__file__, '..', "tw-game.z8"))


@contextlib.contextmanager
def make_temp_directory(suffix='', prefix='tmp', dir=None):
    """ Create temporary folder to used in a with statement. """
    temp_dir = tempfile.mkdtemp(suffix, prefix, dir)
    try:
        yield os.path.join(temp_dir, "")  # So path ends with '/'.
    finally:
        shutil.rmtree(temp_dir)


class TestJerichoGameState(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.game_file = pjoin(cls.tmpdir, "tw-game.z8")
        shutil.copyfile(TEST_GAME, cls.game_file)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def setUp(self):
        self.env = jericho.FrotzEnv(self.game_file)
        self.state = self.env.reset()

    def tearDown(self):
        self.env.close()

    def test_feedback(self):
        game_state, _, _, _ = self.env.step("look")

        # Check feedback for dropping and taking the carrot.
        game_state, _, _, _ = self.env.step("drop carrot")
        assert "drop the carrot on the ground" in game_state
        game_state, _, _, _ = self.env.step("take carrot")
        assert "pick up the carrot from the ground" in game_state

    def test_inventory(self):
        game_state, _, _, _ = self.env.step("inventory")
        game_state, _, _, _ = self.env.step("drop carrot")

        # End the game.
        game_state, _, _, _ = self.env.step("take carrot")
        game_state, _, _, _ = self.env.step("go east")
        game_state, _, _, _ = self.env.step("insert carrot into chest")

        game_state, _, _, _ = self.env.step("close chest")

    def test_description(self):
        game_state, _, _, _ = self.env.step("look")
        game_state, _, _, _ = self.env.step("go east")
        game_state, _, _, _ = self.env.step("look")

        # End the game.
        game_state, _, _, _ = self.env.step("insert carrot into chest")
        game_state, _, _, _ = self.env.step("close chest")

    def test_score(self):
        _, score, _, _ = self.env.step("go east")
        assert score == 0
        _, score, _, _ = self.env.step("insert carrot into chest")
        assert score == 2
        assert self.env.get_max_score() == 3
        _, score, _, _ = self.env.step("close chest")
        assert score == 3

    def test_game_ended_when_no_quest(self):
        game_name = "test_game_ended_when_no_quest"
        with make_temp_directory(prefix=game_name) as tmpdir:
            game_file = pjoin(tmpdir, game_name + ".z8")
            shutil.copyfile(TEST_GAME, game_file)

            env = jericho.FrotzEnv(game_file)
            game_state = env.reset()
            assert not (env.game_over() or env.victory())
            game_state, _, done, _ = env.step("look")
            assert not done
            assert not (env.game_over() or env.victory())
            env.close()

    def test_has_won(self):
        assert not self.env.victory()
        self.env.step("go east")
        assert not self.env.victory()
        self.env.step("insert carrot into chest")
        assert not self.env.victory()
        _, _, done, _ = self.env.step("close chest")
        assert done
        assert self.env.victory()

    def test_has_lost(self):
        assert not self.env.game_over()
        self.env.step("go east")
        assert not self.env.game_over()
        _, _, done, _ = self.env.step("eat carrot")
        assert done
        assert self.env.game_over()


class TestJerichoEnvironment(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.tmpdir = tempfile.mkdtemp()
        cls.game_file = pjoin(cls.tmpdir, "tw-game.z8")
        shutil.copyfile(TEST_GAME, cls.game_file)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmpdir)

    def setUp(self):
        self.env = jericho.FrotzEnv(self.game_file)
        self.game_state = self.env.reset()

    def tearDown(self):
        self.env.close()

    def test_step(self):
        env = jericho.FrotzEnv(self.game_file)
        env.step("look")
        #npt.assert_raises(GameNotRunningError, env.step, "look")

        # TODO: not supported by Jericho
        # # Test sending command when the game has quit.
        # env = textworld.start(self.game_file)
        # env.reset()
        # env.step("quit")
        # env.step("yes")
        # npt.assert_raises(GameNotRunningError, env.step, "look")

        # Test sending empty command.
        env = jericho.FrotzEnv(self.game_file)
        env.reset()
        env.step("")
        env.close()

    def test_loading_unsupported_game(self):
        game_file = pjoin(self.tmpdir, "dummy.z8")
        shutil.copyfile(self.game_file, game_file)

        env = jericho.FrotzEnv(game_file)
        game_state = env.reset()
        assert self.env.get_max_score() == 0

        self.env.step("go east")
        self.env.step("insert carrot into chest")
        game_state, _, done, _ = self.env.step("close chest")

        assert "The End" in game_state
        # assert not game_state.game_ended
        # assert not game_state.has_won
        # assert not game_state.has_lost
        env.close()
