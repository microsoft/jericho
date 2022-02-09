import os
import textwrap
import argparse
from pprint import pprint
from difflib import SequenceMatcher

import numpy as np
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
        270: "wait",  # The cave is now closed.
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
        ]
    },
    "anchor.z8": {
        '*': [
            39, 40, 41,  # Sleeping sequence
            243, 244, 245,  # While sleeping.
            259, # Some light shine through a small hole in the wall.
            303, # From deep within the forest, you hear the deranged cry of a lone whippoorwill.
            317, 318, 319, 320,  # The sound of tearing undergrowth grows louder.
            328,  # The townsfolk advances upon you.
            340, 341,  # The church stairs are about to break.
            376,  # The flashlight turns off and is wet.
            395, 458,  # The match burns down.
            401,  # Ticking sound after lowering the hatch's handle.
            402,  # The hatch's handle snaps back to an upright position.
            431, 432,  # Last night transition
            472, 473,  # The crowd and the bum are arriving to Town Square.
            475,  # Amulet is placed in the scene.
            476, 477,  # The crowd and the bum are leaving Town Square.
            480, 481,  # Run away from monster.
            497,  # Micheal takes a torch from the crowd.
            504,  # Summing sequence, the crowd and guards leave the scene.
            505,  # Micheal leaves.
            509,  # Island of flesh is removed from play.
            513,  # Boy is moving from Shanty Town to Mill Town Road.
            526, 527,  # Ending sequence
        ],
        "ignore_commands": [
            "examine wooden", "examine tall",  # Examining fence enables going through it.
            "examine book",  # Examining book initiate conversation with Micheal
            "examine typewritten", "examine notice",  # Examining notice enables new topic of conversation?
            "examine paintings", "examine scene",  # One scene in particular catches your eye.
            "examine bottles",
            "examine footprints", "examine ground", "examine pattern",
            "examine corpse", "examine real", "examine woman's", "examine decapitated",  # Set Attr8 of Obj245: decapitated corpse
            "examine vats", "examine machinery", "examine machines", "examine floor", "examine presses",  # Set Attr8 of Obj487: mill machinery
            "examine notes",  # Pick up the printed memo.
            "examine little",  # Ends the game.
        ],
    },
    "awaken.z5": {},
    "balances.z5": {
        '*': [
            71,  # A tortoise-feather flutters to the ground before you!
        ],
        "ignore_commands": [
            "examine furniture",  # Discover a cedarwood box.
            "examine oats", "examine pile", "examine of",  # Discover a shiny scroll.
            "examine perfect sapphire", "examine sapphire", "examine perfect",  # Causes to break the sapphire and learn the caskly spell.
        ],
    },
    "ballyhoo.z3": {
        "*": [
            6, 7, 8,  # Listening to the conversation with Munrab.
            40, 41, 62, 88, 122, 125, 126, 249,  # Turnstile's state changes.
            44,  # the trailer door is slammed shut.
            48, 49,  # You get kicked out of the trailer by Chuckles.
            64,  # Observe the detective fo through the turnstile.
            110, 111, 112, 113,  # Lion stand state changes.
            149,  # Right next to the long line a much shorter line begins to form.
            152,  # Jerry yelling to a group of people.
            153,  # You get pushed aside.
            200, 214,  # The tape stops rewinding.
            225,  # Not moving, causes you to die.
            226, 227,  # headphones being reduced to dust in the ape's tense grip.
            253,  # Hannibal of the Jungle thunders out of the tent
            260,  # You can hear someone, presumably Mr. Munrab, barge into the office.
            275, 281, 289, 293, # The spring-loaded secret panel slides shut
            278, 279, # Playing cards
            285,  # Comrade Thumb arrives.
            290, 291, 292, # Dealer and Billy are moving.
            297, 298, 299, 300, 301, # Ladder is being moved.
            342,  # Gottfried arrives
            356, 357,  # Chelsea moves
            361,  # Follow Chelsea.
            368, 369,  # roustabout comes sprinting
            415, # Game ending (slip off the wire).
        ],
        "ignore_commands": [
            "examine flower",  # the daisy spritzes some water in your face
            "examine garbage",  # find an unmarked ticket
            "examine chandelier", "examine leather", "examine sofa",  # Rimshaw the Incomparable speaks
            "examine spreadsheet",  # Discover Chuckles' real name.
            "examine Comrade Thumb",  # You can see a trembling midget hand pull the tablecloth back down.
            "examine andrew",  # Triggering Turnstile (addr. 9113)
        ],
    },
    "curses.z5": {
        '*': [
            386, # Waiting to get caught after triggering the alarm.
            387, # Arriving in the Coven Cell -> This sets Attr8 for rself and Coven Cell.
            648, # Waiting for the bomb's timer runs out.
            673, # Waiting for the magnesium-flare flash at the lighthouse.
            721, # Waiting for the messenger-boy comes feed the pigeons.
            838, # Waiting for the Napoleonic officers to arrive.
            843, # Waiting for the Napoleonic officers to tweak the nose of the sphinx.
            918, # Doing something else causes the hand to fall off the knight.
            921, # Doing something else causes the skull to fall off the knight.
            877, 878, 879, # enter coffin (You are so distracted that common sense takes over and you clamber out of the mummy case.)
            1024,  # druidical figure sequence
            1032,  # Waiting for the Sazon spy to show up.
            1063, 1064, 1065, # Ending
        ],
        "ignore_commands": [
            "examine mirror", "examine vanity", "examine long", "examine long vanity mirror",  # The monkey leaps from your arms, revelling in its new life
            "examine book", "examine poetry", "examine books", "examine a",  # teleports you to Unreal City.
            "examine sheets", "examine pile",  # exposes the radio.
            "examine rolls", "examine insulation",  # discovers a battery.
            "examine agricultural", "examine implement", "examine bladed", # changes the name of the object to "spade".
        ],
        "ignore_objects": [
            111,  # antiquated wireless (i.e., a radio)
            58,  # Austin the cat walking around.
            114,  # Jemima (Jemima hums along)
            211,  # Cups Glasses (look -> hear noise and voices)
            371,  # flurries ofeen luminescence (appearing or fading away)
            401, # skiff (drifting)
            394, # InsideOrb (The sphere rotates and displays images.)
        ]
    },
    "cutthroat.z3": {
        '*': [
            13, 14, 15,  # Weasel arrives and leaves the player's location.
            69,  # Talking with Johnny Red.
            92, 93, 94, 95, 96,  # Waiting for Johnny Red.
            104,  # McGinty
            133, 134, 135, 136,  # Ferry arrives and leaves.
            203,  # Causes a lot of changes.
            204,  # Causes hunger.
            251, 252, # Weasel moves.
            262,  # Causes hunger.
            285,  # The sharks get you.
        ],
        "wait": [
            5, 6, 7, 8, 9, 10, 11, 12,  # You begin to feel hungry.
            105,  # Causes hunger.
            210, 211, 212, 213, 244, 245, 246, 248,  # Weasel's movements
            250, 253,  # boat moves with you and other objects on it.
            254, 255, 256, 257, 258, 259, 260, 261,  # Causes hunger.
        ],
    },
    "deephome.z5": {
        '*': [
            14,  # Dark Spirit arrives.
            184, # scraps become a cohesive whole, melting together
            303, # The gold coin is getting ready.
        ],
        "ignore_commands": [
            "examine patch",  # You find a perfect four leaf clover.
        ],
    },
    "detective.z5": {},
    "dragon.z5": {
        '*': [
            54, 55,  # Troll is coming in.
        ],
        "ignore_commands": [
            "examine remains", "examine barrels",  # You have found a pewter mug
            "examine hollow tree stump", "examine hollow", "examine stump", "examine tree",   # You have found a box of matches
            "examine reeds",  # You have found a sack
            "examine booklet",  # Needed to win the game.
            "examine hessian", "examine brown hessian sack",  # Finds a flute.
            "examine bones", "examine pile",  # Finds a green glass bottle.
            "examine glass",  # Finds a parchment.
        ],
    },
    "enchanter.z3": {
        '*': [
            148,  # You get dragged to the Cell.
            150,  # You get dragged to the Sacrificial Altar.
            176, 177, 178, 179, 180, 181,  # The Adventurer moves.
            204, 205,  # Lurking evil presence is around.
            262, 263, 264,  # The warlock Krill kills you.
        ],
        "wait": [
            67,  # Hearing a voice.
            68,  # group of four hunched and hairy shapes walks into your presence
            149,  # You get killed in the Cell.
            175,  # The Adventurer leaves the room.
        ],
        "ignore_commands": [
            "examine tracks",  # Needed for progression.
            "examine walls",  # Needed for progression.
        ],
    },
    "enter.z5": {
        '*': [
            5,  # Mr. Alltext starts to leave the cafeteria but talks to you.
            15,  # Judy arrives.
            37,  # Stephanie leaves.
            207,  # A bell rings as the package arrives.
        ],
    },
    "gold.z5": {
        "ignore_commands": [
            "examine ash",
            "examine rotting", "examine skeleton",  # Takes the blackened metal poker.
            "examine sludge",  # Finds a small key.
        ],
    },
    "hhgg.z3": {
        '*': [
            11, 12,  # Bulldozer arrives.
            13,  # Prefect arrives
            15,  # Conversation with Prosser
            17,  # Prefect leaves.
            34,  # fleet VogConstructor ships arrive
            35,  # electronic Sub-Etha signaling device arrives
            47,  # "thing aunt gave you which you don't know it is" comes back into the inventory.
            48,  # Gets to the Vogon Hold.
            58,  # Brought to the Captain's Quarters.
            64, 69, 74,  # Brought to the airlock.
            83,  # Going to the Bridge.
            85,  # Zaphod, Ford, and Trillian all head off to port.
            90,  # Marvin arrives.
            96, 97, 98, 99,  # Need to answer a question.
            114,  # "thing aunt gave you which you don't know it is" comes back
            176, 177, 178, 179,  # In the void.
            187,  # Phil arrives and you end up in the Dark.
            201, 202, 203, 204, 205, 206,  # In the void
            212,  # Engineer robot asked a question.
            224, 225, 226, 227, 228,  # In the void.
            243,  # Trillian leaps out of the crowd
            262, 263,  # In the void.
            269,  # The game expects the word "idiot".
            280, 281,  # fleet VogConstructor ships arrive
            282,  # electronic Sub-Etha signaling device arrives
            283,  # In the void
            294, 295, 296, 297, 298, 299, 300, 301, 302,  # In the void
            307,  # Transported to the Maze
            351, 352,  # Marvin is opening the hatch.
        ],
        "look": [
            101, # Ignore the game trying to make you not look.
        ],
        "examine room": [
            101, # Ignore the game trying to make you not look.
        ],
        "wait": [
            16,
            37,  # Earth is destroyed.
            45,  # "thing aunt gave you which you don't know it is" appears into your gown.
            46, 47,  # Ford gives you the Hitchhiker's Guide to the Galaxy.
            88, 89, 93,  # Marvin arrives.
            136,  # Suddenly a team of Fronurbdian Beasthunters charges in
            155,  # Announcement.
            182,  # Arthur talks to hostess.
            331,  # Plant is growing.
        ],
        "ignore_commands": [
            "examine shadow",  # get teleported to Vogon Hold
            "examine Eddie (shipboard computer)",
            "examine arthur", "examine dent", # Reveals ball of fluff on Arthur's jacket.
        ],
    },
    "hollywood.z3": {
        "*": [
            9, 10,  # Tanks are moving.
            39,  # strip of film falls onto the floor.
            311,  # Red match goes out.
            334,  # Green match goes out.
            339,  # the rope it snaps
            385,  # Water drains out.
            387, 388, 389, 390, 391, 392, 393,  # Herman grabs and swings things at you.
        ],
        "wait": [
            310,  # Red match goes out.
            376,  # Closet door swings shut
            383, 384,  # Water drains out.
        ],
    },
    "huntdark.z5": {
        "*": [
            3,  # Player arrives to Bottom of Pit.
            18,  # Player arrives to (Maze).
        ],
    },
    "infidel.z3": {
        "*": [
            7,  # large crate lands right before you
            59,  # match went out.
        ],
        "wait": [
            58,  # match went out.
        ],
        "ignore_commands": [
            "examine all",
            "examine jeweled", "examine jeweled ring", "examine ring",  # Reveals a tiny needle.
        ],
    },
    "inhumane.z5": {
        "*": [
            13,  # the pit collapse, ... you end up in the desert again.
            54,  # the door swings shut.
            84,  # you get pushed off the swinging platform.
        ],
        "ignore_commands": [
            "examine toilet", "examine Roboff's toilet",  # find a dark hole in the toilet.
            "examine pyramid", "examine obelisk", "examine stone",  #  mind is numbed and full of RAHN's strange commandments
        ]
    },
    "jewel.z5": {
        "*": [
            21,  # 'x moss' triggered a clarifying question.
            60,  # Geyser erupts.
            164,  # Dragon attacks you.
            178,  # Sit on the dragon.
            180, 182,  # Dragon moves with you on top of it.
            184,  # Dragon opens the lava gate.
            185,  # You arrive in the Red Dragon's Lair.
            194,  # eastern wall from which the river flows finally gives way
            200,  # surprisingly rejuvenated dragon leaps towards you
            208,  # You're bobbing up and down in a river of cold black water.
            211,  # You arrive at the Pebble Beach
        ],
    },
    "karn.z5": {
        "*": [
            133,  # The thrusters are moved to the Plain.
            148,  # A spacecraft arrives outside the TARDIS.
            255,  # Cybermen arrives.
            256,  # Explosion
            308,  # The firework goes off.
            309, 310, 311,  # Cyberman is coming in.
            312,  # Plastic Button pops back up.
            313,  # Cyberman gets you.
        ],
    },
    "library.z5": {
        "ignore_commands": [
            "examine printers",  # You take the Encyclopedia Frobozzica.
        ],
    },
    "loose.z5": {
        "*" : [
            # 5,  # The wolf loiters in the area, keeping an eye on you.
            # 8,  # The wolf loiters in the area, keeping an eye on you.
            11,  # Need to answer to "Who's there."
            12,  # bungalow door slams open and a voice shouts
            48, 49,  # Ending sequence.
        ],
        "ignore_commands": [
            "examine ladder",  # let you borrow the ladder
            "examine corner",  # you find a tranished brass key
        ],
    },
    "lostpig.z8": {
        "*": [
            87,  # Gnome examines the book with a missing page.
            118,  # Gnome put the missing page back into the book.
            123, 124, 125, 126,  # Pig is eating the bricks.
        ],
        "examine west": [
            23,  # Describes the picture on the west wall (new topics).
        ],
        "examine east": [
            23, 24,  # Describes the picture on the east wall (new topics).
        ],
        "examine south": [
            14, 15, 16, 17, 18, 19, 20,  # Maps to "examine curtain" (see below)
        ],
        "ignore_commands": [
            "examine stairs", "examine metal",  # reveals the whistle and enables a new topic.
            "examine coin",  # Enables a new topic.
            "examine curtain",  # Reveals a way out of cave.
            "examine block", "examine stone",  # Reveals mark on the side of the block.
            "examine hat", "examine little",  # Enable topic about hat.
            "examine box", "examine dent",  # Reveal a lever (enable topics).
            "examine gnome",  # New topics: dress, clos, hair, ear, nose.
            "examine chest", "examine keyhole",  # New topic: key.
            "examine book",  # New topic: mark
            "examine big",  "examine paper",  # New topic: piece paper
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
            "read blueprint",
            "ask bum about himself", "ask bum about anna", "ask bum about crypt", "tell bum about skull",
            "put mirror 1 in caliper"
        ],
        "wait": [
            400,  # Waiting to hear something from within the hatch.
            471, 474,  # Waiting for the old man to meet his faith.
            494,  # Waiting for Michael to ask for the mirror.
            498, 499, 500, 501, 502, 503,  # Summoning sequence.
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
            "buy candy from hawker",  # Doesn't work. Need to give the money instead.
            "look into cage", "look into wagon", "search desk",
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
        "look": [107],  # Needed to time the actions.
        "yes": [92, 93, 94, 95],  # Waiting for Johnny Red.
        "wait": [  # Needed to time the actions.
            12, 46,
            105, 106,  # Wait for McGinty to leave.
            129, 130, 131, 132, 133, 134, 136,  # Wait for the ferry to arrive and leave.
            148, 150, 152, 188, 189, 190, 191,
            194, # Waiting for delivery boy.
            214, 215, 216, 217, 218,  # Waiting for Johnny Red to ask you the coordinates.
        ],
        "noop": [
            "i",
            "read envelope",  # Not needed to complete the game.
            "look in closet",
            "examine plate",
            "look through window",
            "look under bunk",
            "examine compressor",
            "examine air tank",
            "examine glass case",
            "examine stamps",
        ]
    },
    "deephome.z5": {
        "wait": [13, 183],  # Needed to time the actions.
        "noop": [
            "read letter", "read warning note",
            "ask man about hammer", "ask man about eranti",
            "read sign", "ask spirit for name",
            "examine hatch", "examine cabinet", "search table",
            "x door", "x generator", "x terrock", "x pipe", "x panel",
            "x box", "x chest",
            "look up terrock in leshosh", "look up kebarn in leshosh",
            "look up partaim in fresto", "look up indanaz in leshosh",
            "look up ternalim in fresto", "look up cholok in leshosh",
            "look up yetzuiz in fresto", "look up squirrel in leshosh",
        ]
    },
    "detective.z5": {
        "noop": [
            "read paper", "read note",
            "inventory",
        ]
    },
    "dragon.z5": {
        "noop": [
            "break bottle",
            "examine table", "examine parchment", "examine chair",
            "examine carvings", "examine goblin",
        ]
    },
    "enchanter.z3": {
        16: "read scroll",  # Not actually needed for learning the spell.
        202: "read map",  # Not actually needed for completing the game.
        30: "examine it",  # Not actually needed for completing the game.
        "wait": [84],  # Needed to time the actions.
        "look": [127],
        "noop": [
            "read shredded scroll", "read crumpled scroll", "read faded scroll",
            "read damp scroll", "read of unseen terror", "read frayed scroll",
            "read gold leaf scroll", "read stained scroll", "read brittle scroll",
            "read black scroll", "read powerful scroll", "read vellum scroll",
            "read ornate scroll",
            "examine post",
            "examine dusty book",
        ]
    },
    "enter.z5": {
        6: "1",  # Could also say nothing, i.e. '0'.
        20: "read list",  # Not needed to complete the game.
        62: "w",  # Not needed to complete the game.
        "noop": [
            "look at mural",
            "look at list",
        ],
    },
    "gold.z5": {
        146: "open washing machine",  # (door is jammed)
        178: "plug in television",  # (already plugged in)
        179: "watch television",  # (nothing on the screen)
        198: "watch television",  # (cookery programme)
        166: "cut cable", # (too rusty)
        260: "get magic porridge pot",  # (too big)
        340: "get bearskin rug",  # (already have that)
        "noop": [
            "inventory", "look",
            "ask pedlar about suitcase", "ask fairy godmother about horse",
            "ask pedlar about beans", "ask wolf about pigs",
            'ask fairy godmother about cinderella',
            "examine vegetable plot", "examine packet",
            "examine plant pots", "examine table", "examine fireplace",
            "examine dresser", "examine washing machine",
            "examine mousetrap", "examine porridge oats",
            "examine wardrobe", "get dumbells", 'examine tiny metal',
            'examine fusebox', 'examine volt meter', 'examine switch a',
            'examine switch b', 'examine large chair', 'examine electrodes',
            'examine television', 'examine remote control', 'examine dining table',
            'examine toaster', 'examine toaster', 'read leaflet',
            'read instructions', 'examine bench', 'examine dynamite',
            'examine huge bed', 'examine snooker table', 'examine pockets',
        ],
    },
    "hhgg.z3": {
        56: "push switch",  # Not needed to complete the game.
        "wait": [
            14,
            28, 29, 30, 31, 32, 33, 34,  # waiting for fleet VogConstructor ships
            38, 39, 40, 41, # In the void.
            57,  # Announcement
            59, 60, 61, 62, 63,  # Waiting for Vogon to read poetry.
            65, 66, 67, 68, # Waiting for Vogon to read poetry (second verse).
            72, 73,  # Waiting to be thrown into the airlock.
            77, 78, 79, 80,  # In the void.
            84,  # Conversation.

        ],
        "noop": [
            "look", "wait", "z",
            "inventory", "i",
            "look shelf",
            "examine thumb",
            "examine memorial",
            "examine plant",
        ]
    },
    "hollywood.z3": {
        133: "read business card",  # Not needed to complete the game.
        149: "put it on yellowed paper",  # (revealing drawing of a maze) Not actually needed for completing the game.
        348: "read plaque",  # Not needed for completing the game.
        376: "wait",  # Waiting for the closet's door to swing shut.
        383: "read note",  # Not needed to complete the game.
        "wait": [
            375,  # waiting for the closet door to swings shut.
        ],
        "noop": [
            "examine model", "examine film projector", "examine safe",
            "examine red statuette", "examine white statuette", "examine blue statuette",
            "examine lights",
            "put it on yellowed paper",  # Display the maze.
            "read plaque", "read note",
            "read business card"
        ],
    },
    "huntdark.z5": {
        "noop": [
            "wait",  # Waiting for the bat to show the way out.
            "x bats",
            "x pool",
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
        "noop": {
            "examine slot",
        },
    },
    "inhumane.z5": {
        "z": [
            59, 60, 61, 63, 64, 65, 76, 77, 78, 79, 80, 81, 83,  # Timing movement with the swinging platform.
        ],
    },
    "jewel.z5": {
        22: "smell dirty floor",  # Not needed to complete the game.
        91: "get treasure",  # Not needed to complete the game.
        124: "read book",  # Not needed to complete the game.
        125: "ask allarah about white",  # Not needed to complete the game.
        127: "ask allarah about red",  # Not needed to complete the game.
        128: "ask allarah about jewel",  # Not needed to complete the game.
        151: "ask dragon about trinket",  # Not needed to complete the game.
        152: "ask dragon about white",  # Not needed to complete the game.
        153: "ask dragon about black",  # Not needed to complete the game.
        154: "ask dragon about red",  # Not needed to complete the game.
        169: "show crossbow to dragon",
        "z": [
            58, 59,  # Geyser
            160, 161, 162, 163,  # Waiting for the Dragon to be annoyed.
            176, 177, 179, 181, 182, 183,  # Dragon is flying around with you on it.
            187, 188, 189, 190, 191, 192, 193,  # Black dragon spews acid on you.
            206, 207, 209, 210,  # River pushes you.
        ],
        "noop": [
            "i", "look",
            "read label", "read book",
            "x minerals", "x gaping", "x outcrop", "x insect", "x skeleton",
            "x block", "x dragon", "x fungus", "x mushroom", "x crossbow",
            "x body", "x salt", "x door", "x murals", "x mirror", "x pedestal",
            "x porous wall", "x bladder", "x ariana", "x boots", "x lye", "x coat",
            "x chandelier",
            "search refuse", "search boots",
            "look under cushion",
        ],
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
            "z",
            'x homing', 'x scanner', 'x tree', 'x k9', 'x bubble',
            'x plate', 'x left screen', 'x right screen', 'look up',
            'x control', 'x mine', 'x door', 'x device', 'x apparatus',
            'x respirator', 'x vent', 'x console', 'x slot', 'x creature',
            'x globe',
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
        "noop": [
            'i',
            'x attendant', 'x librarian', 'x stairs', 'x painting',
            'x technician', 'x shelves', 'x magazines',
        ]
    },
    "loose.z5": {
        "noop": [
            "ask mary for ladder",
        ],
    },
    "lostpig.z8": {
        15: "follow pig",
        28: "wear hat",
        36: "smell brick",
        52: "listen",
        58: "look under bed",
        61: "look under bed",
        62: "open trunk",  # It's looked.
        64: "take ball",
        79: "open chest",  # Grunk not have any key.
        88: "ask gnome about page",
        94: "take thing",
        95: "cross river",
        98: "take water",
        109: "take paper",
        110: "take paper with pole",
        122: "z",  # Waiting for to eat the brick.
        139: "north",  # It too dark, and tunnel look twisty.
        145: "thank gnome",
        "noop": [
            "look",
            'inventory',
            'look inside tube', 'x brick', 'x coin', 'x crack', 'x dent',
            'x fountain', 'x hand', 'x key', 'x man', 'x pig', 'x shadow',
            'x thing', 'x chair', 'x farm', 'x forest', 'x pole', 'x windy tunnel',
            'x top shelf', 'x hat', 'x river', 'x ball', 'x shelf',
        ],
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
    "spirit.z5": {
        "noop": ["z"],
        5: "read note",
        15: "read prayer",
        31: "read diary",
        35: "read page",
        38: "read journal",
        44: "read faded",
        55: "read scriptures",
        56: "consult scriptures about planes",
        63: "read paper",
        156: "read notice",
        184: "read ledger",
        185: "read subway",
        188: "ask governor about key",
        204: "read news in newspaper",
        206: "read features in newspaper",
        210: "z",  # Waiting for the train.
        251: "read cracked",
        270: "ask delbin about ale",
        271: "ask morgan about dragon",
        298: "z",  # Waiting for the doors to close.
        300: "z",  # Waiting for the train to stop.
        316: "read history book",
        350: "w",  # Some strange invisible force stops you
        359: "read journal",
        361: "read research paper",
        "z": [
            *range(373, 378+1),  # In the train.
            *range(380, 385+1),  # In the train.
        ],
        397: "read journal",
        408: "read sign",
        432: "read map",
        506: "ask skier about scroll",
        531: "gnusto bekdab",  # First attempt fails.
        579: "read memo",
        624: "read sign",
        651: "ask delbin about minirva",
        756: "read sign",
        1065: "read ripped",
        1109: "read scrawled",
        1120: "read blackened",
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
    },
    "zork1.z5": {
        56: "read book",
        214: "read label",  # FROBOZZ MAGIC BOAT COMPANY
    },
    "zork2.z5": {
        "wait": [167, 168, 169, 238, 239]  # Needed to time the actions.
    },
    "zork3.z5": {
        "wait": [
            # Needed for the indicator to cycle through I, II, III, and IV.
            29, 30, 31, 35,
            60, 61,  # Not needed.
            64, 65, 66,  # Waiting to hear a voice.
            *range(72, 80+1),  # Waiting for an old boat to pass alongside the shore.
            *range(85, 99+1),
            139, 140, 141, 142, 143,  # Waiting for guard to march away
        ],
        135: "read plaque",
        262: "read book",
    },
    "ztuu.z5": {}
}


def display_diff(A, B):
    s = SequenceMatcher(None, A, B)

    line1, line2 = "", ""
    prev_match = None
    for match in s.get_matching_blocks():
        if prev_match:
            line1 += colored(A[prev_match.a+prev_match.size:match.a], "red")
            line2 += colored(B[prev_match.b+prev_match.size:match.b], "red")

        line1 += A[match.a:match.a+match.size]
        line2 += B[match.b:match.b+match.size]

        prev_match = match

    print(line1)
    print(line2)


def test_walkthrough(env, walkthrough, verbose=False):
    env.reset()
    for i, cmd in enumerate(walkthrough):
        obs, score, done, info = env.step(cmd)
        if verbose:
            print(colored(f"{i}. > {cmd}\n{obs}", "yellow"))

    if not env.victory():
        msg = "FAIL\tScore {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'red'))
        return False
    elif info["score"] != env.get_max_score():
        msg = "FAIL\tDone but score {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'yellow'))
        return False
    else:
        msg = "PASS\tScore {}/{}".format(info["score"], env.get_max_score())
        print(colored(msg, 'green'))
        return True


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

    commands_to_ignore = []
    triggered_ram_addrs = set()
    walkthrough = env.get_walkthrough()
    env_ = env.copy()
    for i, cmd in tqdm(list(enumerate(walkthrough))):
        cmd = cmd.lower()
        last_hash = env.get_world_state_hash()

        precheck_state = (args.check_state and not args.no_precheck and i >= args.skip_to
                          and cmd not in SKIP_PRECHECK_STATE.get(rom, {}).get(i, {})
                          and i not in SKIP_PRECHECK_STATE.get(rom, {}).get("*", []))

        state = env.get_state()
        env_.set_state(state)
        if precheck_state:
            objs = env_._identify_interactive_objects(use_object_tree=True)
            cmds = ["look", "inventory", "wait", "examine me", "asd"]
            cmds += ["examine " + obj[0][0] for obj in objs.values()]
            for cmd_ in cmds:
                skip_precheck_state = (
                    cmd_ in SKIP_PRECHECK_STATE.get(rom, {}).get(i, [])
                    or cmd_ in SKIP_PRECHECK_STATE.get(rom, {}).get("ignore_commands", [])
                    or i in SKIP_PRECHECK_STATE.get(rom, {}).get(cmd_, [])
                )

                if skip_precheck_state:
                    continue

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

                if skip:
                    break

                if env_._world_changed():
                    objs1 = env.get_world_objects(clean=False)
                    objs2 = env_.get_world_objects(clean=False)

                    # for o1, o2 in zip(objs1, objs2): print(colored(f"{o1}\n{o2}", "red" if o1 != o2 else "white"))
                    print(colored(f'{i}. [{cmd_}]: world hash has changed.\n"""\n{obs_}\n"""', 'red'))
                    for o1, o2 in zip(env_objs, env_objs_):
                        if o1 != o2:
                            display_diff(str(o1), str(o2))

                    rams1 = env._get_special_ram()
                    rams2 = env_._get_special_ram()
                    if any(rams1 != rams2):
                        pprint(dict(zip(env_._get_ram_addrs(), np.array([rams1, rams2]).T)))

                    breakpoint()
                    break

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
            if env._world_changed():

                if env.frotz_lib.get_special_ram_changed() and not env.frotz_lib.get_objects_state_changed():
                    ram_addrs = env._get_ram_addrs()
                    ram_old = env_._get_special_ram()
                    ram_new = env._get_special_ram()
                    for ram_addr, value_old, value_new in zip(ram_addrs, ram_old, ram_new):
                        if value_old != value_new:
                            triggered_ram_addrs.add(ram_addr)

            else:
                print(colored(f'{i}. [{cmd}]: world hash hasn\'t changed.\n"""\n{obs}\n"""', 'red'))

                print("Objects diff:")
                for o1, o2 in zip(last_env_objs, env_objs):
                    if o1 != o2:
                        display_diff(str(o1), str(o2))

                print("Cleaned objects diff:")
                for o1, o2 in zip(last_env_objs_cleaned, env_objs_cleaned):
                    if o1 != o2:
                        display_diff(str(o1), str(o2))

                # For debugging.
                print(f"Testing walkthrough without '{cmd}'...")
                alt1 = test_walkthrough(env.copy(), walkthrough[:i] + walkthrough[i+1:])
                print(f"Testing walkthrough replacing '{cmd}' with 'wait'...")
                alt2 = test_walkthrough(env.copy(), walkthrough[:i] + ["wait"] + walkthrough[i+1:])
                # print(f"Testing walkthrough replacing '{cmd}' with '0'...")
                # alt3 = test_walkthrough(env.copy(), walkthrough[:i] + ["0"] + walkthrough[i+1:])
                # print(f"Testing walkthrough replacing '{cmd}' with 'wait 1 minute'...")
                # alt4 = test_walkthrough(env.copy(), walkthrough[:i] + ["wait 1 minute"] + walkthrough[i+1:])
                print(f"Testing walkthrough replacing '{cmd}' with 'look'...")
                alt5 = test_walkthrough(env.copy(), walkthrough[:i] + ["look"] + walkthrough[i+1:])

                if all((alt1, alt2, alt5)):
                    commands_to_ignore.append(cmd)
                else:
                    breakpoint()

    not_triggered_ram_addrs = set(env._get_ram_addrs()) - triggered_ram_addrs
    if not_triggered_ram_addrs:
        msg = "-> Special RAM not used: " + repr(sorted(not_triggered_ram_addrs))
        print(colored(msg, "yellow"))

    if commands_to_ignore:
        msg = "-> Walkthrough commands that can be safely ignored: " + repr(sorted(set(commands_to_ignore)))
        print(colored(msg, "yellow"))

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
