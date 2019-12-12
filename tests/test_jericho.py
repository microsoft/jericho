import os
import warnings
from os.path import join as pjoin

import jericho
from jericho import MultipleInstancesWarning


DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))


def test_multiple_instances():
    gamefile = pjoin(DATA_PATH, "905.z5")
    with warnings.catch_warnings(record=True) as w:
        env1 = jericho.FrotzEnv(pjoin(DATA_PATH, gamefile))
        env2 = jericho.FrotzEnv(pjoin(DATA_PATH, gamefile))
        assert len(w) == 1
        assert issubclass(w[-1].category, MultipleInstancesWarning)

        env1 = jericho.FrotzEnv(pjoin(DATA_PATH, "905.z5"))
        env2 = jericho.FrotzEnv(pjoin(DATA_PATH, "905.z5"))
        env1.reset()  # Resetting env1 also affects env2.

        assert "Are you sure you want to quit?" in env1.step("quit")[0]
        # The state of env2 has been affected by env1.step
        assert "Please answer yes or n" in env2.step("look")[0]
        env1.close()

    with warnings.catch_warnings(record=True) as w:
        env1 = jericho.FrotzEnv(pjoin(DATA_PATH, gamefile))
        env1.reset()
        env1.close()  # Closing first env to avoid warning.
        env2 = jericho.FrotzEnv(pjoin(DATA_PATH, gamefile))
        assert len(w) == 0
