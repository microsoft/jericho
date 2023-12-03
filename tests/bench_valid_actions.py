import sys
import time
import argparse

from tqdm import tqdm
from termcolor import colored

import jericho


def run(rom, args, use_ctypes=False, use_parallel=False):
    env = jericho.FrotzEnv(rom)
    walkthrough = env.get_walkthrough()
    start = time.time()
    valid_per_step = []

    limit = args.limit or len(walkthrough)
    for act in tqdm(walkthrough[:limit]):
        valid_acts = env.get_valid_actions(use_ctypes=use_ctypes, use_parallel=use_parallel)
        valid_per_step.append(valid_acts)

    elapsed = time.time() - start
    env.close()
    return elapsed, valid_per_step


def compare(rom, args):
    t1, gt_valids = run(rom, args)
    t2, pred_valids_c = run(rom, args, use_ctypes=True)
    t3, pred_valids_para = run(rom, args, use_parallel=True)
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


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames",
                        help="Path to a Z-Machine game.", nargs="+")
    parser.add_argument("--limit", metavar="K", type=int,
                        help="Stop comparison after the first K commands.")

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    for rom in args.filenames:
        print(f"\n-=# {rom} #=-")
        compare(rom, args)
