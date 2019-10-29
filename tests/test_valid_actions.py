import os
from os.path import join as pjoin
import jericho
from jericho.template_action_generator import TemplateActionGenerator

DATA_PATH = os.path.abspath(pjoin(__file__, '..', "data"))

def test_valid_action_identification():
    rom_path = pjoin(DATA_PATH, '905.z5')
    env = jericho.FrotzEnv(rom_path)
    bindings = load_bindings(rom_path)
    act_gen = TemplateActionGenerator(bindings)
    obs, info = env.reset()
    # interactive_objs = [obj[0] for obj in env.identify_interactive_objects(use_object_tree=True)]
    interactive_objs = ['phone', 'keys', 'wallet']
    candidate_actions = act_gen.generate_actions(interactive_objs)

    valid = env.find_valid_actions(candidate_actions)
    assert 'take wallet' in valid
    assert 'open wallet' in valid
    assert 'take keys' in valid
    assert 'get up' in valid
    assert 'take phone' in valid
