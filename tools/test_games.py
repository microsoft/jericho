import os
import textwrap
import argparse

from termcolor import colored
import jericho


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", nargs="+",
                        help="Path to a Z-Machine game(s).")
    parser.add_argument("--debug", action="store_true",
                        help="Launch ipdb on FAIL.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    return parser.parse_args()

args = parse_args()

filename_max_length = max(map(len, args.filenames))
for filename in sorted(args.filenames):
    print(filename.ljust(filename_max_length), end=" ")

    env = jericho.FrotzEnv(filename)
    if not env.is_fully_supported:
        print(colored("SKIP\tUnsupported game", 'yellow'))
        continue

    if "walkthrough" not in env.bindings:
        print(colored("SKIP\tMissing walkthrough", 'yellow'))
        continue

    env.reset()

    #walkthrough = bindings['walkthrough'].split('/')
    for cmd in env.get_walkthrough():
        obs, rew, done, info = env.step(cmd)

    if not done:
        print(colored("FAIL", 'red'))
        if args.debug:
            from ipdb import set_trace; set_trace()
    elif info["score"] != env.get_max_score():
        msg = "FAIL\tDone but score {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'red'))
        if args.verbose:
            print(textwrap.indent(obs, prefix="  "))

        if args.debug:
            from ipdb import set_trace; set_trace()
    else:
        print(colored("PASS", 'green'))
