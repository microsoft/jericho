import os
import sys

import argparse
import readline

import jericho


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filename",
                        help="Path to a Z-Machine game.")
    parser.add_argument("--walkthrough",
                        help="External walkthrough (one command per line). Default: use Jericho's one, if it exists.")
    parser.add_argument("--skip-to", type=int, default=0,
                        help="Auto-play walkthrough until the nth command before dropping into interactive mode.")

    return parser.parse_args()

args = parse_args()

history = []
env = jericho.FrotzEnv(args.filename)
obs, info = env.reset()

history.append(env.get_state())

STEP_BY_STEP_WALKTRHOUGH = True

walkthrough = env.get_walkthrough()
if args.walkthrough:
    walkthrough = []
    for line in open(args.walkthrough):
        cmd = line.split("#")[0].strip()
        if cmd:
            walkthrough.append(cmd)

obs_list = [obs]
commands = []
cpt = 0
while True:
    if STEP_BY_STEP_WALKTRHOUGH and cpt < len(walkthrough):
        cmd = walkthrough[cpt]
        print(obs)
        if cpt >= args.skip_to:
            alt = input("{}. [{}] > ".format(cpt, cmd))
            if alt:
                cmd = alt
        else:
            print("{}. [{}]".format(cpt, cmd))
    else:
        print(obs)
        cmd = input("{}. > ".format(cpt))

    if cmd == "undo":
        history = history[:-1]
        commands = commands[:-1]
        obs_list = obs_list[:-1]
        env.set_state(history[-1])
        obs = obs_list[-1]
        cpt -= 1
    elif cmd == "debug":
        from ipdb import set_trace; set_trace()
    elif cmd == "break":
        break
    else:
        obs, rew, done, info = env.step(cmd)
        commands.append(cmd)
        obs_list.append(obs)
        history.append(env.get_state())
        cpt += 1

print()
print("/".join(commands).replace('"', '\\"'))
