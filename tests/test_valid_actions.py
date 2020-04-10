import os
from os.path import join as pjoin
import jericho

DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))

def test_valid_action_identification():
    rom_path = pjoin(DATA_PATH, '905.z5')
    env = jericho.FrotzEnv(rom_path)
    obs, info = env.reset()
    valid = env.get_valid_actions()
    assert 'take wallet' in valid
    assert 'open wallet' in valid
    assert 'take keys' in valid
    assert 'get up' in valid
    assert 'take phone' in valid
