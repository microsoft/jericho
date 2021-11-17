import os
import textwrap
import argparse

import numpy as np
from tqdm import tqdm
from termcolor import colored

import jericho


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", nargs="+",
                        help="Path to a Z-Machine game(s).")
    parser.add_argument("--index", type=int, help="Index of the walkthrough command to investigate.")
    parser.add_argument("--interactive", action="store_true",
                        help="Type the command.")
    parser.add_argument("--debug", action="store_true",
                        help="Launch ipdb on FAIL.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    parser.add_argument("-vv", "--very-verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    parser.add_argument("--check-state", action="store_true",
                        help="Check if each command changes the state.")
    return parser.parse_args()

args = parse_args()


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


filename_max_length = max(map(len, args.filenames))
for filename in sorted(args.filenames):
    rom = os.path.basename(filename)
    print(filename.ljust(filename_max_length))#, end=" ")

    env = jericho.FrotzEnv(filename)
    if not env.is_fully_supported:
        print(colored("SKIP\tUnsupported game", 'yellow'))
        continue

    if "walkthrough" not in env.bindings:
        print(colored("SKIP\tMissing walkthrough", 'yellow'))
        continue

    env.reset()
    Z = get_zmp(env)

    history = []
    history.append((0, 'reset', env.get_state(), Z))

    walkthrough = env.get_walkthrough()
    cmd_no = 0

    noise_indices = set()
    relevant_indices = set()
    changes_history = []
    cpt = 0
    while True:
        if cmd_no >= len(walkthrough):
            break

        cmd = walkthrough[cmd_no].lower()

        if args.interactive:
            manual_cmd = input(f"{cpt}. [{cmd}]> ")
            if manual_cmd.strip():
                cmd = manual_cmd.lower()
        else:
            print(f"{cpt}. > {cmd}")

        if cmd == walkthrough[cmd_no].lower():
            cmd_no += 1

        last_env_objs = env.get_world_objects(clean=False)
        last_env_objs_cleaned = env.get_world_objects(clean=True)

        last_Z = Z
        obs, rew, done, info = env.step(cmd)
        cpt += 1
        # print(">", cmd)
        print(obs)

        env_objs = env.get_world_objects(clean=False)
        env_objs_cleaned = env.get_world_objects(clean=True)

        Z = get_zmp(env)

        changes = set(np.nonzero(Z != last_Z)[0])

        history.append((cmd, env.get_state(), Z))
        changes_history.append(changes)

        # ans = ""
        # while ans not in {'y', 'n', 's'}:
        #     ans = input("State has changed? [y/n/s]> ").lower()

        # if ans == "y":
        #     relevant_indices |= changes - noise_indices
        # elif ans == "s":
        #     pass
        # elif ans == "n":
        #     noise_indices |= changes
        #     relevant_indices -= noise_indices
        # else:
        #     assert False

        #print(special_indices)

        # display_relevant(Z, changes, relevant_indices, noise_indices)

        def display_objs_diff():
            print("Objects diff:")
            for o1, o2 in zip(last_env_objs, env_objs):
                if o1 != o2:
                    print(colored(f"{o1}\n{o2}", "red"))

            print("Cleaned objects diff:")
            for o1, o2 in zip(last_env_objs_cleaned, env_objs_cleaned):
                if o1 != o2:
                    print(colored(f"{o1}\n{o2}", "red"))

        # breakpoint()

    def search_unique_changes(idx):
        counter = {idx: 0 for idx in changes_history[idx]}
        matches = {idx: [] for idx in changes_history[idx]}
        for i, changes in enumerate(changes_history):
            for idx in changes:
                if idx in counter:
                    counter[idx] += 1
                    matches[idx].append((i, history[i+1][0], history[i+1][2][idx]))

        for idx, count in sorted(counter.items(), key=lambda e: e[::-1]):
            # if matches[idx][0][0] == 0:
                # continue

            print(f"{idx:6d}: {count:3d} : " + ", ".join(f"{i}.{cmd}({value})" for i, cmd, value in matches[idx][:20]))

    #if len(changes_history) > :
    print(f"Ram changes unique to command: {args.index}. > {history[args.index+1][0]}")
    search_unique_changes(args.index)
    # display_indices(search_unique_changes(args.index))
    if args.debug:
        breakpoint()
