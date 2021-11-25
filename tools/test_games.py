import os
import textwrap
import argparse

from tqdm import tqdm
from termcolor import colored

import jericho


SKIP_PRECHECK_STATE = {
    "905.z5": { },
    "acorncourt.z5": {},
    "adventureland.z5": {
        "ignore_objects": [
            49,  # chigger bites (You get bitten by chiggers.)
            45,  # evil smelling mud (The mud dried up and fell off.)
            71,  # large African bees (The bees in the bottle all suffocated.)
        ]
    },
    "advent.z5": {
        39: "yes",  # Answering 'With what? Your bare hands?'.
        167: "u",  # Otherwise the dwarf kills the player.
        169: "u",  # Otherwise the dwarf kills the player.
        180: "d",  # Otherwise the dwarf kills the player.
        202: "u",  # Otherwise the dwarf kills the player.
        270: "u",  # Otherwise the dwarf kills the player.
        '*': range(270, 276+1),  # Waiting. Nothing happens.
        'ignore_objects': [
            264,  # Little Dwarf
            265,  # Little axe
            268,  # endgame_timer (prop 40)
        ]
    },
    "afflicted.z8": {
        "*": [5, 6],  # Angela is moving and unlocking the door.
        'ignore_objects': [
            143,  # Ice (The ice has completely melted.)
            204, 205, 206, 207,  # no-name objects.
        ]
    },
    "anchor.z8": {
        '*': [
            1, 2, 3,  # Examining fence enables going through it.
            15,  # Examining book initiate conversation with Micheal
            26, 27,  # Examining notice enables new topic of conversation?
            39, 40, 41,  # Sleeping sequence
            77,  # Examine paintings (One scene in particular catches your eye).
            78,  # Examine scene.
            243, 244, 245,  # While sleeping.
            259, # Some light shine through a small hole in the wall.
            277, # Examine wine bottles
            303, # From deep within the forest, you hear the deranged cry of a lone whippoorwill.
            317, 318, 319,  # The sound of tearing undergrowth grows louder.
            400,  # Ticking sound after lowering the hatch's handle.
            431,  # Last night transition
            513,  # Boy is moving from Shanty Town to Mill Town Road.
            521,  # Micheal is strangling you.
            526,  # Ending sequence

        ],
        'ignore_objects': [
            141,  # Train (at time 0, the train is put on Obj129 Railroad Tracks.)
            158,  # pale, frightened woman (prop 40)
            210,  # (gang)
            221,  # Footprints (set attr 8)
            245,  # decapitated corpse (set attr 8)
            251,  # church_stairs (prop 41)
            252,  # Broken Stairs (clear attr 24)
            370,  # Flashlight (clear attr 9 and 13)
            372,  # book of matches (clear attr 9)
            395,  # Wine Cellar (prop 40)
            471,  # hatch (clear attr 11)
            472,  # metal handle (clear attr 8)
            487,  # mill machinery (set attr 8)
            496,  # printed memo (move to player's inventory)
            509,  # Top of the Lighthouse (change prop 41)
            516,  # Island of Flesh (change prop 41)
            27,  # (appearence) (change prop 41)
            462,  # ghost of Croseus Verlac (change prop 41 - counter for battle sequence?)
            467,  # pressure gauge (prop 41)
            231,  # Home (change prop 41 - Micheal asking about pregnancy test)
        ],
    },
    "awaken.z5": {},
    "balances.z5": {
        '*': [
            20, 21,  # Examining the sapphire causes it to break.
            109, 110  # The cyclops is losing patience.
        ],
        "ignore_objects": [
            57,  # Shiny scroll (examining the pile of oats gives you the scroll).
            51,  # cedarwood box (examining the furniture gives you the box)
            67,  # tortoise feather (A tortoise-feather flutters to the ground before you!)
            65,  # (lobal_spell) (prop 40)
            86,  # buck-toothed cyclops (prop 40)
        ]
    },
    "ballyhoo.z3": {
        "*": [
            6, 7, 8, # Listening to the conversation with Munrab.
            41, 62, 88, 122, 125, 126, 249,  # Turnstile's state changes.
            110, 111, 112, 113,  # Lion stand state changes.
            278, 279,  # Playing cardsrn
            200, 214, # Rewinding the tape
            260, 261, 262, 263, 264, 265, # Sequence for "search desk" (addr. 8629).
            266, # Examining the spreadsheet triggers (addr. 8845).
            297, 298, 299, 301, # Ladder is being moved.
            396, 405, 406, # Triggering Turnstile (addr. 9113)
            415, # Game ending (slip off the wire).
        ],
        "ignore_objects": [
            113,  # Chuckles is moving around.
            122,  # ticket is revealed while examining the garbage
            20,  # leatsofa (examine leather, set attr 12)
            78,  # hawker appears
            17,  # short line (Right next to the long line a much shorter line begins to form.)
            162,  # Jerry
            42,  # groballplayers
            211,  # it
            142,  # concessistand (you see the line you first entered suddenly kicking into gear)
            163,  # one-dollar-and-85-cent granola bar (examine garbage -> picks it up)
            9,  # Mahler (screams, clear attr 12)
            141,  # elephant (thunders out of the tent)
            175,  # Menagerie (set attr 18)
            95,  # blackjack table (set attr 12)
            212,  # secret panel (attr 15, opens/closes it)
            219,  # Comrade Thumb (appears in the room)
            116,  # dealer (appears/disappears)
            300,  # elephant prod (moving)
            218,  # Gottfried Wilhelm vKatzenjammer (moving)
            84,  # Chelsea (moving)
        ]
    },
    "curses.z5": {
        '*': [
            877, 878, 879, # enter coffin (You are so distracted that common sense takes over and you clamber out of the mummy case.)
            1024,  # druidical figure sequence
            1063, 1064, 1065, # Ending
        ],
        "z": [386, 387],  # Waiting
        "ignore_objects": [
            111,  # antiquated wireless
            76,  # new-lookty (examine insulation -> discover battery)
            58,  # Austin the cat walking around.
            114,  # Jemima (Jemima hums along)
            154,  # Unreal City (examine book/poetry -> transport you?!)
            298,  # spade (examine agricultural -> let's just call a spade a spade.)
            216,  # model ship (examine ship -> you pick it up from force of habit)
            211,  # Cups Glasses (look -> hear noise and voices)
            195,  # Coven Cell (look -> attr 8, prop 23.)
            309,  # beanle (look -> prop 23)
            2,  # north (moving from compass to flagpole?!)
            371,  # flurries ofeen luminescence (fading away)
            200,  # glass cabinet
            70,  # book of Twentiesetry (examine book/poetry -> transport you?!)
            206, # timer-detonator (timer runs out)
            205, # complicated-look bomb (counter prop 23)
            396, # Causeway (counter prop 23)
            448, # BirdcagfMuses (counter prop 23)
            401, # skiff (drifting)
            420, # Napoleonic officers (appears)
            496, # adamantinend (The hand wobbles and falls off the knight again.)
            432, # adamantinkull (The skull wobbles and falls off the knight again.)
            394, # InsideOrb (attr 8)
            353, # Tentle (prop 23)
            354, # Saxon spy appears
            355, # Encampment (prop 23)

        ]
    },

}

SKIP_CHECK_STATE = {
    "905.z5": {},
    "acorncourt.z5": {
        13: "look in bucket",  # State didn't change.
    },
    "adventureland.z5": {},
    "advent.z5": {
        52: "nw",  # Random outcome, state didn't change.
        'wait': range(255, 276+1),  # Nothing happens.
    },
    "afflicted.z8": {
        "noop": [
            "search grate",  # Like a examine.
            "search window",  # Like a examine.
            "note it",  # Need to open the chopper and examine the blade
            "open cover",  # The cover is held in place by a large screw.
            "turn screw",  # The screw is rusted in place.
            "read killing",  # You read: Killing Vampires
            "read culture",  # You read: Vampire Culture
            "ask angela about affliction",  # Angela whispers, ..., I think.
        ]
    },
    "anchor.z8": {
        "noop": [
            "read newspaper",# "read news in newspaper", "read sports in newspaper", "read features in newspaper",
            "Look up Wilhelm in album", #"Look up Eustacia in album", "Look up Croseus in album",
            "read slip of paper",
            "read wall",
            "ask bum about himself", "ask bum about anna", "ask bum about crypt", "tell bum about skull",
            "put mirror 1 in caliper"
        ]
    },
    "awaken.z5": {
        4: "n",  # Dog blocks your path.
        "noop": [
            "read book",  # Read the book on the pulpit.
            "read old book",  # Read the old grimoire on the bookshelf in the Small Office.
        ]
    },
    "balances.z5": {
        "noop": [
            "wait",  # Nothing happens.
            "listen",  # Not needed.
        ]
    },
    "ballyhoo.z3": {
        "noop": [
            "wait",  # You hear a loud growl nearby.
            "ask pitchman about dr nostrum",  # Not needed to complete the game.
            "read note",  # Not needed to complete the game.
        ]
    },
    "curses.z5": {
        868: "turn sceptre",  # Stochastic outcome. The word didn't change.
        873: "turn sceptre",  # Stochastic outcome. The word didn't change.
        875: "turn sceptre",  # Stochastic outcome. The word didn't change.
        "noop": [
            "z", "wait",  # wave splashes against the sea front.
            "read romance novel",  # Not needed to complete the game.
            "read about alison in history book",  # Not needed to complete the game.
            "read inscription",  # Not needed to complete the game.
            "read letter",  # Not needed to complete the game.
            "read tombstone",  # Not needed to complete the game.
        ]
    },
    "cutthroat.z3": {
        1: "wind watch",  # Could be replaced by wait.
        "wait": [12, 132, 133, 150, 190, 191, 216, 217, 218],  # Needed to time the actions.
        "noop": [
            "read envelope",  # Not needed to complete the game.
        ]
    },
    "deephome.z5": {
        "wait": [13, 183],  # Needed to time the actions.
        "noop": [
            "read letter",  # Not needed to complete the game.
            "read warning note",  # Not needed to complete the game.
            "ask man about hammer",  # Not needed to complete the game.
            "ask man about eranti",  # Not needed to complete the game.
            "read sign",  # Not needed to complete the game.
            "ask spirit for name",  # Not needed to complete the game.
        ]
    },
    "detective.z5": {
        "noop": [
            "read paper",  # Not needed to complete the game.
            "read note",  # Not needed to complete the game.
        ]
    },
    "dragon.z5": {
        "noop": [
            "break bottle",  # Not needed to complete the game.
        ]
    },
    "enchanter.z3": {
        16: "read scroll",  # Not actually needed for learning the spell.
        202: "read map",  # Not actually needed for completing the game.
        "wait": [84],  # Needed to time the actions.
        "noop": [
            "read shredded scroll",  # Not needed to complete the game.
            "read crumpled scroll",  # Not needed to complete the game.
            "read faded scroll",  # Not needed to complete the game.
            "read damp scroll",  # Not needed to complete the game.
            "read of unseen terror",  # Not needed to complete the game.
            "read frayed scroll",  # Not needed to complete the game.
            "read gold leaf scroll",  # Not needed to complete the game.
            "read stained scroll",  # Not needed to complete the game.
            "read brittle scroll",  # Not needed to complete the game.
            "read black scroll",  # Not needed to complete the game.
            "read powerful scroll",  # Not needed to complete the game.
            "read vellum scroll",  # Not needed to complete the game.
            "read ornate scroll",  # Not needed to complete the game.
        ]
    },
    "enter.z5": {
        6: "1",  # Could also say nothing, i.e. '0'.
        20: "read list",  # Not needed to complete the game.
        62: "w",  # Not needed to complete the game.
    },
    "gold.z5": {
        146: "open washing machine",  # (door is jammed) Not needed to complete the game.
        178: "plug in television",  # (already plugged in) Not needed to complete the game.
        179: "watch television",  # (nothing on the screen) Not needed to complete the game.
        309: "ask fairy godmother about horse",  # Not needed to complete the game.
    },
    "hhgg.z3": {
        56: "push switch",  # Not needed to complete the game.
        "noop": [
            "z", "wait", # Needed to time the actions.
        ]
    },
    "hollywood.z3": {
        133: "read business card",  # Not needed to complete the game.
        149: "put it on yellowed paper",  # (revealing drawing of a maze) Not actually needed for completing the game.
        348: "read plaque",  # Not needed for completing the game.
        376: "wait",  # Waiting for the closet's door to swing shut.
        383: "read note",  # Not needed to complete the game.
    },
    "huntdark.z5": {
        "noop": [
            "wait",  # Waiting for the bat to show the way out.
        ]
    },
    "infidel.z3": {
        9: "read note",  # Not needed to complete the game.
        26: "drink water",  # Not needed to complete the game.
        129: "read hieroglyphs",  # Not needed to complete the game.
        145: "read hieroglyphs",  # Not needed to complete the game.
        159: "read hieroglyphs",  # Not needed to complete the game.
        173: "read hieroglyphs",  # Not needed to complete the game.
        184: "read scroll",  # Not needed to complete the game.
    },
    "inhumane.z5": {},
    "jewel.z5": {
        22: "smell dirty floor",  # Not needed to complete the game.
        91: "get treasure",  # Not needed to complete the game.
        124: "read book",  # Not needed to complete the game.
        125: "ask allarah about white",  # Not needed to complete the game.
        127: "ask allarah about red",  # Not needed to complete the game.
        128: "ask allarah about jewel",  # Not needed to complete the game.
    },
    "karn.z5": {
        46: "read sign",  # Not needed to complete the game.
        93: "ask k9 about k9",  # Not needed to complete the game.
        155: "k9, follow me",  # Not needed to complete the game.?
        163: "ask k9 about door",  # Not needed to complete the game.
        232: "ask k9 about door",  # Not needed to complete the game.
        237: "ask k9 about reactor",  # Not needed to complete the game.
        238: "ask k9 about control",  # Not needed to complete the game.
        239: "ask k9 about sequence",  # Not actually needed for completing the game (important information).
        320: "ask k9 about cybermen",  # Not needed to complete the game.
        "noop": [
            "z"
        ],
    },
    "library.z5": {
        2: "read tag",  # Not needed to complete the game.
        3: "ask alan about novel",  # Not needed to complete the game.
        4: "ask him about nelson",  # Not needed to complete the game.
        5: "ask him about librarian",  # Not needed to complete the game.
        8: "read tag",  # Not needed to complete the game.
        9: "ask marion about nelson",  # Not needed to complete the game.
        10: "ask her about rare books",  # Not needed to complete the game.
        11: "ask her about key",  # Not needed to complete the game.
        13: "ask alan about key",  # Not needed to complete the game.
        19: "smell",  # Not needed to complete the game.
        41: "ask marion about encyclopedia",  # Not needed to complete the game.
        50: "ask technician about security gates",  # Not needed to complete the game.
    },
    "loose.z5": {},
    "lostpig.z8": {
        15: "follow pig",  # Not needed to complete the game.
        28: "wear it",  # Not needed to complete the game.
        36: "smell it",  # Not needed to complete the game.
        52: "listen",  # Not needed to complete the game.
        94: "take thing",  # Not needed to complete the game.
        95: "cross river",  # Not needed to complete the game.
        98: "take water",  # Not needed to complete the game.
        109: "take paper",  # Not needed to complete the game.
        110: "take paper with pole",  # Not needed to complete the game.
    },
    "ludicorp.z5": {
        7: "smell car",  # Not needed to complete the game.
        50: "open door",  # (it is locked) Not needed to complete the game.
        140: "shoot window",  # (glass is bulletproof) Not needed to complete the game.
        239: "play arcade",  # (you died) Not needed to complete the game.
        241: "play pool",  # (no ball nor cues) Not needed to complete the game.
        255: "w",  # (outer airlock door blocks your way) Not needed to complete the game.
    },
    "lurking.z3": {
        "noop": ["z"]
    },
    "moonlit.z5": {},
    "murdac.z5": {},
    "night.z5": {
        37: "get printer",  # Not needed to complete the game.
        38: "ask gnome about printer",  # Not needed to complete the game.
        "noop": ["z"]
    },
    "omniquest.z5": {},
    "partyfoul.z8": {
        "z": [53, 54],  # Ending sequence.
    },
    "pentari.z5": {},
    "planetfall.z3": {
        216: "eat brown goo",  # Not needed to complete the game.
    },
    "plundered.z3": {
        # 11: "z",  # Dialog. [Press RETURN or ENTER to continue.]
        61: "cut line with dagger",  # Not needed.
        106: "read label",  # Not needed.
        116: "give garter to papa",  # Not needed.
        129: "n",  # Not needed.
        131: "z",  # Not needed.
        151: "z",  # Not needed.
    },
    "reverb.z5": {
        1: "read note",  # Not needed.
        "z": [50, 51],  # Not needed.
    },
    "seastalker.z3": {
        4: "ask bly about problem",  # Not needed.
        5: "ask bly about monster",  # Not needed.
        11: "ask computestor about videophone",  # Not needed.
        18: "ask kemp about circuit breaker",  # Not needed.
        27: "push test button",  # Not needed.
        28: "read sign",  # Not needed.
        105: "e",  # Can't go.
        128: "s",  # Can't go.
        151: "s",  # Too crowded. Have to wait.
    },
    "sherlock.z5": {
        "wait": [75],  # Needed to time the actions.
        9: "read paper",
        34: "ask holmes about ash",  # Can be replaced with 'wait 1 minute'.
        159: "open book",  # The librarian launches off into another speech.
        162: "read book",  # Not actually needed.
        179: "read sign",  # Not actually needed.
        232: "read plaque",  # Not actually needed.
        238: "n",  # Guard stops you and ask not to bribe them.
        318: "ask for akbar",  # Denkeeper is asking for the password.
    },
    "snacktime.z8": {},
    "sorcerer.z3": {
        "wait": [138, 139],  # Needed to time the actions.
        12: "read journal",  # Can be replaced with 'wait'.
        26: "read dusty scroll",  # meef spell: cause plants to wilt
        32: "read moldy scroll",  # aimfiz spell: transport caster to someone else's location
        42: "read shiny scroll",  # gaspar spell: provide for your own resurrection
        53: "read soiled scroll",  # fweep spell: turn caster into a bat
        111: "read parchment scroll",  # swanzo spell: exorcise an inhabiting presence
        169: "read ordinary scroll",  # yonk spell: augment the power of certain spells
        193: "read glittering scroll",  # malyon spell: bring life to inanimate objects
        225: "read shimmering scroll",  # golmac spell: travel temporally
    },
    "spellbrkr.z3": {
        "z": [1, 2, 16, 42, 43, 44, 107, 108, 109, 110, 111, 112, 142, 233, 234, 235, 236, 300, 301, 302],  # Needed to time the actions.
        23: "read stained scroll",  # caskly spell: cause perfection
        34: "read flimsy scroll",  # girgol spell: stop time
        39: "read dirty scroll",  # throck spell: cause plants to grow.
        80: "read dusty scroll",  # espnis spell: sleep.
        99: "read damp scroll",  # liskon spell: shrink a living thing.
        157: "read white scroll",  # tinsot spell: freeze.
        162: "point at blue carpet",
        197: "read moldy book",  # snavig spell: shape change
        330: "ask belboz about cube",
        331: "ask belboz about figure",
        368: "read vellum scroll",  # empty
    },
    "temple.z5": {
        32: "ask charles about temple",
        77: "ask charles about chest",
        84: "listen",
    },
    "theatre.z5": {
        "z": [15],
        "wait": [15, 249],
        190: "read newspaper",
        271: "show earth crystal to trent",
        272: "show star crystal to trent",
        274: "ask trent about elizabeth",
    },
    "trinity.z4": {
        28: "read paper",
        56: "read card",
        83: "reach in sculpture",
        154: "read crypt",
        155: "open crypt",
        180: "talk to boy",
        184: "knock on door",
        233: "put honey in cauldron",
        376: "point at coconut",  # Needed to time the actions.
        573: "wait",
    },
    "tryst205.z5": {
        5: "ask george about bag",
        6: "ask george about beetlebaum",
        7: "ask george about frank",
        13: "open bag",  # The zipper is too rusted to move.
        47: "read label",
        70: "shake safe",  # There is something rattling around in there.
        71: "open safe",  # Concentrate as you may, but you can't come up with the combination.
        90: "s",  # The mosquitos and gnats start to eat you alive, forcing you to leave while you still can.
        96: "read sign",  # The mosquitos and gnats start to eat you alive, forcing you to leave while you still can.
        111: "s",  # You can't, since the jail door is in the way.
        129: "read green",
        136: "clean table with cloth",  # You move the dust around with the dry cloth, but not much else.
        138: "read crumpled",
        141: "set second wheel to 2",  # Second wheel already set to 2.
        188: "read writing",
        192: "n",  # You can't, since the livery door is in the way.
        193: "open door",  # It seems to be locked.
        228: "read note",
        244: "read sign",
        245: "read book",
        253: "ask george about dehlila",
        254: "ask george about gumball",
        255: "ask george about town",
        387: "read lettering",
        404: "read sign",
        444: "read sign",
        448: "read plaque",
        496: "wait",  # Waiting to be not invisible anymore.
    },
    "weapon.z5": {
        9: "touch information",  # ... better not activate it unless you've got some way to stop her.
        56: "pull rods",  # .. you can not do anything else while holding them together...
    },
    "wishbringer.z3": {
        38: "wait",  # Waiting for the curtain to open.
    },
    "yomomma.z8": {
        "talk to sleaze": [24, 25, 26, 27],
        54: "put coin in jukebox",  # Not needed.
        60: "n",  # When you feel you're ready to challenge Gus again you can CLIMB ON STAGE.
        68: "n",  # When you feel you're ready to challenge Gus again you can CLIMB ON STAGE.
        88: "put coin in jukebox",  # Not needed.
    },
    "zenon.z5": {
        44: "n",  # cannot pass without proper paperwork!
        45: "ask male about female",
        46: "ask male about work",
        47: "ask male about officer",
        48: "ask male about invitation",
        49: "ask male about daddy",
        50: "ask female about male",
        51: "ask female about bar",
    }

}


def test_walkthrough(env, walkthrough):
    env.reset()
    for cmd in walkthrough:
        obs, score, done, info = env.step(cmd)

    if not env.victory():
        msg = "FAIL\tScore {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'red'))
    elif info["score"] != env.get_max_score():
        msg = "FAIL\tDone but score {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'yellow'))
    else:
        msg = "PASS\tScore {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'green'))


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("filenames", nargs="+",
                        help="Path to a Z-Machine game(s).")
    parser.add_argument("--interactive", action="store_true",
                        help="Type the command.")
    parser.add_argument("--skip-to", type=int, default=0,
                        help="Do not perform checks before the ith command.")
    parser.add_argument("--debug", action="store_true",
                        help="Launch ipdb on FAIL.")
    parser.add_argument("--debug-at", type=int,
                        help="Launch after the ith command.")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    parser.add_argument("-vv", "--very-verbose", action="store_true",
                        help="Print the last observation when not achieving max score.")
    parser.add_argument("--check-state", action="store_true",
                        help="Check if each command changes the state.")
    parser.add_argument("--no-precheck", action="store_true",
                        help="Skip checking 'examine <obj>' actions.")
    return parser.parse_args()

args = parse_args()


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

    obs, _ = env.reset()

    if args.very_verbose:
        print(obs)

    # history = []
    # history.append((0, 'reset', env.get_state()))

    walkthrough = env.get_walkthrough()
    for i, cmd in tqdm(list(enumerate(walkthrough))):
        cmd = cmd.lower()
        last_hash = env.get_world_state_hash()

        precheck_state = (args.check_state and not args.no_precheck and i >= args.skip_to
                          and cmd not in SKIP_PRECHECK_STATE.get(rom, {}).get(i, {})
                          and i not in SKIP_PRECHECK_STATE.get(rom, {}).get("*", []))

        if precheck_state:
            env_ = env.copy()
            state = env_.get_state()
            objs = env_._identify_interactive_objects(use_object_tree=True)
            cmds = ["look", "inv"]
            cmds += ["examine " + obj[0][0] for obj in objs.values()]
            for cmd_ in cmds:
                env_.set_state(state)
                obs_, _, _, _ = env_.step(cmd_)

                env_objs = env.get_world_objects(clean=True)
                env_objs_ = env_.get_world_objects(clean=True)
                changed_objs = [o1 for o1, o2 in zip(env_objs_, env_objs) if o1 != o2]

                skip = False
                for obj in changed_objs:
                    if obj.num in SKIP_PRECHECK_STATE.get(rom, {}).get("ignore_objects", []):
                        skip = True
                        break

                # world_diff = env_._get_world_diff()
                # moved_objs, set_attrs, cleared_attrs, changed_props, _ = world_diff
                # skip = False
                # for obj in moved_objs + set_attrs + cleared_attrs + changed_props:
                #     if obj[0] in SKIP_PRECHECK_STATE.get(rom, {}).get("ignore_objects", []):
                #         skip = True
                #         break

                if skip:
                    break

                if env_._world_changed():
                # if last_hash != env_.get_world_state_hash():
                    # env_objs = env.get_world_objects(clean=True)
                    # env_objs_ = env_.get_world_objects(clean=True)
                    objs1 = env.get_world_objects(clean=False)
                    objs2 = env_.get_world_objects(clean=False)

                    # for o1, o2 in zip(objs1, objs2): print(colored(f"{o1}\n{o2}", "red" if o1 != o2 else "white"))
                    print(colored(f'{i}. [{cmd_}]: world hash has changed.\n"""\n{obs_}\n"""', 'red'))
                    for o1, o2 in zip(env_objs, env_objs_):
                        if o1 != o2:
                            print(colored(f"{o1}\n{o2}", "red"))

                    breakpoint()
                    break

                # if env_._world_changed():
                #     print(colored(f'{i}. [{cmd_}]: world state has changed.\n"""\n{obs_}\n"""', 'red'))
                #     breakpoint()

        if args.interactive:
            tmp = input(f"{i}. [{cmd}] >")
            if tmp.strip():
                cmd = tmp

        last_env_objs = env.get_world_objects(clean=False)
        last_env_objs_cleaned = env.get_world_objects(clean=True)

        obs, rew, done, info = env.step(cmd)
        # calls = env.get_calls_stack()
        # print(" -> ".join(map(hex, calls)))

        env_objs = env.get_world_objects(clean=False)
        env_objs_cleaned = env.get_world_objects(clean=True)

        # state = env.get_state()
        # history.append((i, cmd, state))

        if args.very_verbose:
            print(f"{i}. >", cmd)
            print(obs)

            if i == args.debug_at:
                breakpoint()

        check_state = (args.check_state and i >= args.skip_to
                       and cmd not in SKIP_CHECK_STATE.get(rom, {}).get(i, {})
                       and i not in SKIP_CHECK_STATE.get(rom, {}).get(cmd, [])
                       and cmd not in SKIP_CHECK_STATE.get(rom, {}).get('noop', {}))

        if check_state:
            # if not env._world_changed():
            #     print(colored(f'{i}. [{cmd}]: world state hasn\'t changed.\n"""\n{obs}\n"""', 'red'))
            #     breakpoint()

            if not env._world_changed():
            # if last_hash == env.get_world_state_hash():
                if cmd.split(" ")[0] not in {"look", "l", "x", "search", "examine", "i", "inventory"}:

                    print(colored(f'{i}. [{cmd}]: world hash hasn\'t changed.\n"""\n{obs}\n"""', 'red'))

                    print("Objects diff:")
                    for o1, o2 in zip(last_env_objs, env_objs):
                        if o1 != o2:
                            print(colored(f"{o1}\n{o2}", "red"))

                    print("Cleaned objects diff:")
                    for o1, o2 in zip(last_env_objs_cleaned, env_objs_cleaned):
                        if o1 != o2:
                            print(colored(f"{o1}\n{o2}", "red"))

                    print(f"Testing walkthrough without '{cmd}'...")
                    test_walkthrough(env.copy(), walkthrough[:i] + walkthrough[i+1:])
                    print(f"Testing walkthrough replacing '{cmd}' with 'wait'...")
                    test_walkthrough(env.copy(), walkthrough[:i] + ["wait"] + walkthrough[i+1:])
                    print(f"Testing walkthrough replacing '{cmd}' with '0'...")
                    test_walkthrough(env.copy(), walkthrough[:i] + ["0"] + walkthrough[i+1:])
                    print(f"Testing walkthrough replacing '{cmd}' with 'wait 1 minute'...")
                    test_walkthrough(env.copy(), walkthrough[:i] + ["wait 1 minute"] + walkthrough[i+1:])
                    print(f"Testing walkthrough replacing '{cmd}' with 'look'...")
                    test_walkthrough(env.copy(), walkthrough[:i] + ["look"] + walkthrough[i+1:])
                    breakpoint()
            # else:
            #     world_diff = env._get_world_diff()
            #     if len(world_diff[-1]) > 1:
            #         print(colored("Multiple special RAM addressed have been triggered!", 'yellow'))
            #         print(f"RAM: {world_diff[-1]}")
            #         breakpoint()

            # else:
            #     changed_objs = [(o1, o2) for o1, o2 in zip(env_objs_cleaned, last_env_objs_cleaned) if o1 != o2]

            #     world_diff = env._get_world_diff()
            #     if len(changed_objs) > 0 and len(world_diff[-1]) > 0:
            #         print(colored("Special RAM address triggered as well as object modifications!", 'yellow'))
            #         print(colored("Is the special RAM address really needed, then?", 'yellow'))
            #         print(f"RAM: {world_diff[-1]}")
            #         for o1, o2 in changed_objs:
            #             print(o2)  # New
            #             print(o1)  # Old

            #         breakpoint()


    if not env.victory():
        print(colored("FAIL", 'red'))
        if args.debug:
            from ipdb import set_trace; set_trace()
    elif info["score"] != env.get_max_score():
        msg = "FAIL\tDone but score {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'yellow'))
        if args.verbose:
            print(textwrap.indent(obs, prefix="  "))

        if args.debug:
            from ipdb import set_trace; set_trace()
    else:
        msg = "PASS\t Score {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'green'))
