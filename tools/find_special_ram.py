import os
import textwrap
import argparse

import numpy as np
from tqdm import tqdm
from termcolor import colored

import jericho


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename",
                        help="Path to a Z-Machine game.")
    parser.add_argument("--index", type=int, help="Index of the walkthrough command to investigate.")
    parser.add_argument("--alternative-command",
                        help="Type the command to replace the one at '--index'.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    parser.add_argument("-vv", "--very-verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    return parser.parse_args()



def get_zmp(env):
    zmp = env.get_state()[0]
    #start = zmp.view(">u2")[6]  # ref: https://inform-fiction.org/zmachine/standards/z1point1/sect06.html#two
    #length = 240 * 2  # 240 2-byte global variables.
    #globals = zmp[start:start + length].view(">i2")
    return zmp


def display_indices(indices):
    indices = sorted(indices)

    NB_COLS = 16
    for row in range(int(np.ceil(len(indices) / NB_COLS))):
        for col in range(NB_COLS):
            idx = (row * NB_COLS) + col
            if idx >= len(indices):
                break

            text = f"{indices[idx]:6d}"
            print(text, end=",")

        print()


def display_relevant(G, changed, relevant, noise):
    relevant = sorted(relevant)

    NB_COLS = 16
    for row in range(int(np.ceil(len(relevant) / NB_COLS))):
        for col in range(NB_COLS):
            idx = (row * NB_COLS) + col
            if idx >= len(relevant):
                break

            color = 'white'
            # assert len(relevant & noise) == 0
            #if idx in relevant:
            color = 'green'
            if idx in noise:
                color = 'red'

            bg_color = None
            attrs = []
            if idx in changed:
                attrs.append("bold")
                bg_color = "on_grey"

            text = colored(f"{relevant[idx]:5x}", color, bg_color)
            print(text, end=",")

        print()

def display_ram(G, changed, relevant, noise):
    NB_COLS = 150
    for row in range(int(np.ceil(len(G) / NB_COLS))):
        for col in range(NB_COLS):
            idx = (row * NB_COLS) + col
            color = 'white'
            assert len(relevant & noise) == 0
            if idx in relevant:
                color = 'green'
            if idx in noise:
                color = 'red'

            bg_color = None
            attrs = []
            if idx in changed:
                attrs.append("bold")
                bg_color = "on_grey"

            text = colored(f".", color, bg_color)
            print(text, end="")

        print()


def show_mem_diff(M0, M1, M2, start=24985, length=240*2):
    # TODO: start can be obtained from ZMP.view('>i2')[6]
    import numpy as np

    M1 = M1[start:start+length].view(">i2")
    M2 = M2[start:start+length].view(">i2")
    indices = np.nonzero(M1 != M2)[0]

    if M0 is not None:
        M0 = M0[start:start+length].view(">i2")
        to_print = sorted(set(indices) - set(np.nonzero(M0 != M1)[0]))
        to_print += [None]
        to_print += sorted(set(indices) & set(np.nonzero(M0 != M1)[0]))

    for i in to_print:
        if i is None:
            print("--")
            continue

        print(f"{i:3d} [{start+i*2:5d}]: {M1[i]:5d} -> {M2[i]:5d}")


def collect_zmp(env, walkthrough, verbose=False):
    env.reset()
    Z = get_zmp(env)

    history = []
    # history.append((0, 'reset', env.get_state(), Z))
    history.append({"cmd": 'reset', "state": env.get_state(), "zmp": Z})

    cmd_no = 0

    # noise_indices = set()
    # relevant_indices = set()
    # changes_history = []
    cpt = 0
    while True:
        if cmd_no >= len(walkthrough):
            break

        cmd = walkthrough[cmd_no].lower()

        if verbose:
            print(f"{cpt}. > {cmd}")

        if cmd == walkthrough[cmd_no].lower():
            cmd_no += 1

        # last_Z = Z
        obs, _, _, _ = env.step(cmd)
        cpt += 1
        if verbose:
            print(obs)

        Z = get_zmp(env)

        # changes = set(np.nonzero(Z != last_Z)[0])

        history.append({'cmd': cmd, "state": env.get_state(), "zmp": Z})
        # changes_history.append(changes)

    return history#, changes_history


def compute_zmp_changes(history):
    last_Z = history[0]['zmp']
    changes = []
    for state in history[1:]:
        Z = state['zmp']
        changes.append(set(np.nonzero(Z != last_Z)[0]))
        last_Z = Z

    return changes


def display_unique_changes(idx, history, changes_history):
    counter = {idx: 0 for idx in changes_history[idx]}
    matches = {idx: [] for idx in changes_history[idx]}
    for i, changes in enumerate(changes_history):
        for idx in changes:
            if idx in counter:
                counter[idx] += 1
                matches[idx].append((i, history[i+1]["cmd"], history[i+1]["zmp"][idx]))

    for idx, count in sorted(counter.items(), key=lambda e: e[::-1]):
        # if matches[idx][0][0] == 0:
        #     continue

        print(f"{idx:6d}: {count:3d} : " + ", ".join(f"{i}.{cmd}({value})" for i, cmd, value in matches[idx][:20]))


def main():
    args = parse_args()

    env = jericho.FrotzEnv(args.filename)
    print(args.filename)
    if not env.is_fully_supported:
        print(colored("SKIP\tUnsupported game", 'yellow'))
        return

    if "walkthrough" not in env.bindings:
        print(colored("SKIP\tMissing walkthrough", 'yellow'))
        return

    walkthrough = env.get_walkthrough()
    history = collect_zmp(env, walkthrough, verbose=True)
    changes_history = compute_zmp_changes(history)

    print(f"Ram changes unique to command: {args.index}. > {history[args.index+1]['cmd']}")
    if args.alternative_command:
        walkthrough_ = walkthrough[:args.index] + [args.alternative_command] + walkthrough[args.index+1:]
        history2 = collect_zmp(env, walkthrough_, verbose=False)
        changes_history2 = compute_zmp_changes(history2)
        assert len(changes_history) == len(changes_history2)

        for i in range(len(changes_history)):
            changes_history[i] = changes_history[i] & changes_history2[i]

        print(f"intersected with ram changes unique to command: {args.index}. > {args.alternative_command}")


    display_unique_changes(args.index, history, changes_history)


if __name__ == "__main__":
    main()
