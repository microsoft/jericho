"""
Use jericho's template action generator to select random actions
"""
import argparse
import random
from termcolor import colored

from jericho import FrotzEnv


# Create the environment, optionally specifying a random seed
def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("rom_path", help="Path to a Z-Machine game.", type=str,
        default="../../z-machine-games-master/jericho-game-suite/905.z5")
    parser.add_argument( "--max_iterations", type=int,
        help="Maximum number of iterations to allow the agent to run.", default=100)
    parser.add_argument( "--debug", action="store_true", help="Launch ipdb.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    return parser.parse_args()


def get_random_action(env, args):
    valid_actions = env.get_valid_actions()
    chosen_action = random.choice(valid_actions)
    if args.verbose:
        print(colored(("valid actions:", valid_actions), 'green'))
        print(colored(("chosen action:", chosen_action), 'red'))
    return chosen_action


args = parse_args()
env = FrotzEnv(args.rom_path)
obs, info = env.reset()
done = False

while not done:
    if args.debug:
        import ipdb; ipdb.set_trace()
    args.max_iterations -= 1
    if (args.max_iterations < 1):
        print(colored('Max Iterations Exceeded -- BREAK', 'red'))
        break

    # Use TemplateActionGenerator to select an action
    chosen_action = get_random_action(env, args)

    # Take an action in the environment using the step fuction.
    # The resulting text-observation, reward, and game-over indicator is returned.
    observation, reward, done, info = env.step(chosen_action)
    # Total score and move-count are returned in the info dictionary
    if args.verbose:
        print(observation)
    print('Total Score', info['score'], 'Moves', info['moves'])
print('Scored', info['score'], 'out of', env.get_max_score())
