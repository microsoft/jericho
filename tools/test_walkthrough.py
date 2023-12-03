import argparse

from termcolor import colored

import jericho
from jericho.util import clean


def get_detected_hashes(env):
    interactive_objs  = env._identify_interactive_objects(use_object_tree=True)
    best_obj_names    = env._score_object_names(interactive_objs)
    candidate_actions = env.act_gen.generate_actions(best_obj_names)
    hash2acts         = env._filter_candidate_actions(candidate_actions, use_ctypes=True, use_parallel=True)
    return hash2acts


def analyze_step(idx, env, gold_act):
    """
    Checks to ensure the resulting hash from playing the walkthrough action (gold_act) is amoung the state hashes
    considered by get_valid_actions.

    """
    hash2acts = get_detected_hashes(env)
    obs, _, _, _ = env.step(gold_act)
    gold_hash = env.get_world_state_hash()

    if gold_act.startswith('x ') or gold_act.startswith('examine ') or gold_act == 'z':
        return

    if not env._world_changed():
        print(colored('{}. NoWorldChange gold_act: {}, obs: {}'.format(idx, gold_act, clean(obs)), 'magenta'))

    if gold_hash not in hash2acts:
        print(colored('{}. gold_act: {}-{} not in valids. Obs: {}'.format(idx, gold_act, gold_hash, clean(obs)), 'red'))


def run_walkthrough(rom):
    """
    Runs the walkthrough checking for two main things:
        1) Is the state hash from the walkthrough action among the state hashes in get_valid_actions()?
        2) Is the world state hash for the current state been encountered before or is unique?

    """
    env = jericho.FrotzEnv(rom)
    obs, _ = env.reset()
    walkthrough = env.get_walkthrough()
    hashes = {}
    for idx, gold_act in enumerate(walkthrough):
        whash = env.get_world_state_hash()
        if not whash in hashes:
            hashes[whash] = [idx]
        else:
            print(colored('{}: {} States with same hash: {}'.format(idx, obs, hashes[whash]), 'cyan'))
            hashes[whash].append(idx)
        print(f'Step {idx} - {gold_act}')
        analyze_step(idx, env, gold_act)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('rom', type=str, help='Rom File')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    run_walkthrough(args.rom)
