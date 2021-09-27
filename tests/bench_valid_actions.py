import sys
import time
import argparse

from tqdm import tqdm
from termcolor import colored

import jericho


def run(rom, use_ctypes=False, use_parallel=False):
    env = jericho.FrotzEnv(rom)
    walkthrough = env.get_walkthrough()
    start = time.time()
    valid_per_step = []

    for act in tqdm(walkthrough[:5]):
        valid_acts = env.get_valid_actions(use_ctypes=use_ctypes, use_parallel=use_parallel)
        valid_per_step.append(valid_acts)

    elapsed = time.time() - start
    env.close()
    return elapsed, valid_per_step


def compare(rom):
    t1, gt_valids = run(rom)
    t2, pred_valids_c = run(rom, use_ctypes=True)
    t3, pred_valids_para = run(rom, use_parallel=True)
    assert len(gt_valids) == len(pred_valids_c)
    assert len(gt_valids) == len(pred_valids_para)

    for v1, v2 in zip(gt_valids, pred_valids_c):
        false_negs = set(v1) - set(v2)
        false_pos = set(v2) - set(v1)
        for a in false_negs:
            print(f"Act {a} was valid in Python but not in CTypes")
        for a in false_pos:
            print(f"Act {a} was valid in Ctypes but not in Python")

    for v1, v2 in zip(gt_valids, pred_valids_para):
        false_negs = set(v1) - set(v2)
        false_pos = set(v2) - set(v1)
        for a in false_negs:
            print(f"Act {a} was valid in Python but not in Para")
        for a in false_pos:
            print(f"Act {a} was valid in Para but not in Python")

    speedup = 100 * (t1 / t2 - 1)
    print(f"Rom {rom} Python {t1:.1f} Ctypes {t2:.1f} Speedup {speedup:.1f}%")
    speedup = 100 * (t1 / t3 - 1)
    print(f"Rom {rom} Python {t1:.1f} Para {t3:.1f} Speedup {speedup:.1f}%")


KNOWN_MISSING_ACTIONS = {
    "zork1.z5": {56: "read book", 214: "read label", 262: "kill thief with nasty knife", 387: "look", 389: "examine map"}
}


def check_correctness(rom, skip_to=0, verbose=False):
    env = jericho.FrotzEnv(rom)
    env_ = jericho.FrotzEnv(rom)

    walkthrough = env.get_walkthrough()
    env.act_gen.templates

    # Display info about action templates for the game.
    nargs_templates = {0: [], 1: [], 2: []}
    for template in env.act_gen.templates:
        nargs_templates[template.count("OBJ")].append(template)

    print("-= Template categories =-")
    print(f"  {len(env.act_gen.templates)} templates. 0-arg: {len(nargs_templates[0])}, 1-arg: {len(nargs_templates[1])}, 2-arg: {len(nargs_templates[2])}.")
    if verbose:
        print(f"  0-arg ({len(nargs_templates[0])}): {sorted(nargs_templates[0])}")
        print(f"  1-arg ({len(nargs_templates[1])}): {sorted(nargs_templates[1])}")
        print(f"  2-arg ({len(nargs_templates[2])}): {sorted(nargs_templates[2])}")

    start = time.time()

    obs, info = env.reset()
    valid_acts = env.get_valid_actions()

    # class CaptureStdoutForTdqm:
    #     def __init__():

    with tqdm(total=len(walkthrough)) as pbar:
        pbar.set_description(rom)

        for idx, act in enumerate(walkthrough):

            last_state = env.get_state()

            obs, rew, done, info = env.step(act)
            print(idx, act, info, env.get_world_state_hash())
            if idx < skip_to:
                if idx == skip_to - 1:
                    breakpoint()
                    valid_acts = env.get_valid_actions()

                pbar.update(1)
                continue

            found_matching_command = False
            equivalent_commands = []
            for cmd in valid_acts:
                env_.set_state(last_state)
                env_.step(cmd)
                if env_.get_world_state_hash() == env.get_world_state_hash():
                    equivalent_commands.append(cmd)
                    found_matching_command = True

            if found_matching_command:
                pbar.write(f"{idx:02d}. [{colored(act, 'green')}] found in [{', '.join([colored(a, 'green' if a in equivalent_commands else 'white') for a in valid_acts])}]")
            else:
                pbar.write(f"{idx:02d}. [{colored(act, 'red')}] not found in {valid_acts}")
                if act != KNOWN_MISSING_ACTIONS.get(env.story_file, {}).get(idx):
                    print(colored("Unexpected missing action!!!", 'red'))
                    # breakpoint()

            valid_acts = env.get_valid_actions()
            pbar.update(1)

    elapsed = time.time() - start
    print(f"{elapsed:.1f} secs. Score: {info['score']} (Done: {done})")
    env.close()
    return elapsed


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames",
                        help="Path to a Z-Machine game.", nargs="+")
    parser.add_argument("--skip-to", type=int, default=0,
                        help="Auto-play walkthrough until the nth command before dropping into interactive mode.")

    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()

    for rom in args.filenames:
        print(f"\n-=# {rom} #=-")
        check_correctness(rom, args.skip_to)

    # compare(rom)
    # t2, pred_valids_c = run(rom, use_ctypes=True)
    # t3, pred_valids_para = run(rom, use_parallel=True)

    # t2, pred_valids_para = run(rom, use_ctypes=True)
    # t3, pred_valids_para = run(rom, use_parallel=True)

