# Copyright (C) 2018 Microsoft Corporation

# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

import os
import shutil
import tempfile
import warnings
import numpy as np
import hashlib
from . import defines
from . import util as utl
from .template_action_generator import TemplateActionGenerator
from ctypes import *
from numpy.ctypeslib import as_ctypes
from pkg_resources import Requirement, resource_filename

JERICHO_PATH = resource_filename(Requirement.parse('jericho'), 'jericho')
FROTZ_LIB_PATH = os.path.join(JERICHO_PATH, 'libfrotz.so')

# Function to unload a shared library.
dlclose_func = CDLL(None).dlclose  # This WON'T work on Win
dlclose_func.argtypes = [c_void_p]


class ZObject(Structure):
    """
    A Z-Machine Object contains the following fields:

    :param num: Object number
    :type num: int
    :param name: Short object name
    :type name: string
    :param parent: Object number of parent
    :type parent: int
    :param sibling: Object number of sibling
    :type sibling: int
    :param child: Object number of child
    :type child: int
    :param attr: 32-bit array of object attributes
    :type attr: array
    :param properties: object properties
    :type properties: list

    :Example:

    >>> from jericho import *
    >>> env = FrotzEnv('zork1.z5')
    >>> env.get_player_object()
    Obj4: cretin Parent180 Sibling181 Child0 Attributes [7, 9, 14, 30] Properties [18, 17, 7]

    """
    _fields_ = [("num",        c_int),
                ("_name",      c_char*64),
                ("parent",     c_int),
                ("sibling",    c_int),
                ("child",      c_int),
                ("_attr",      c_byte*4),
                ("properties", c_ubyte*16)]

    def __init__(self):
        self.num = -1

    def __str__(self):
        return "Obj{}: {} Parent{} Sibling{} Child{} Attributes {} Properties {}"\
            .format(self.num, self.name, self.parent, self.sibling, self.child,
                    np.nonzero(self.attr)[0].tolist(), [p for p in self.properties if p != 0])

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        # Equality check doesn't compare siblings and children. This
        # makes comparison among object trees more flexible.
        if isinstance(self, other.__class__):
            return self.num   == other.num      and \
                self.name     == other.name     and \
                self.parent   == other.parent   and \
                self._attr[0] == other._attr[0] and \
                self._attr[1] == other._attr[1] and \
                self._attr[2] == other._attr[2] and \
                self._attr[3] == other._attr[3] and \
                self.properties[:] == other.properties[:]
        return False

    def __hash__(self):
        return hash(str(self))

    @property
    def name(self):
        return self._name.decode('cp1252')

    @property
    def attr(self):
        return np.unpackbits(np.array(self._attr, dtype=np.uint8))


class DictionaryWord(Structure):
    """
    A word recognized by a game's parser.

    :param word: The dictionary word itself.
    :type word: string
    :param is_noun: Is the word a noun.
    :type is_noun: boolean
    :param is_verb: Is the word a verb.
    :type is_verb: boolean
    :param is_prep: Is the word a preposition.
    :type is_prep: boolean
    :param is_meta: Used for meta commands like 'verbose' and 'script'
    :type is_meta: boolean
    :param is_plural: Used for pluralized nouns (e.g. bookcases, rooms)
    :type is_plural: boolean
    :param is_dir: Used for direction words (e.g. north, aft)
    :type is_dir: boolean
    :param is_special: Used for special commands like 'again' which repeats last action.
    :type is_special: boolean

    :Example:

    >>> from jericho import *
    >>> env = FrotzEnv('zork1.z5')
    >>> vocab = env.get_dictionary()
    [$ve, ., ,, ", a, across, activa, advent, ... zork, zorkmi, zzmgck]
    >>> [w for w in vocab if w.is_noun]
    [advent, advert, air, air-p, altar, art, aviato, ax, axe, bag, ... ]
    >>> [w for w in vocab if w.is_adj]
    [ancien, antiqu, bare, beauti, birds, black, bloody, blue, ... ]

    .. note:: Many parsers will recognize only the first six or nine characters of\
    each word. For example `northwest` is functionally equivalent to `northw`.

    .. warning:: Not all games specify the parts of speech for dictionary words.

    """
    _fields_ = [("_word",      c_char*10),
                ("is_noun",    c_bool),
                ("is_verb",    c_bool),
                ("is_prep",    c_bool),
                ("is_meta",    c_bool),
                ("is_plural",  c_bool),
                ("is_dir",     c_bool),
                ("is_adj",     c_bool),
                ("is_special", c_bool)]

    def __init__(self, word, is_noun=False, is_verb=False,
                 is_prep=False, is_meta=False, is_plural=False,
                 is_dir=False, is_adj=False, is_special=False):
        super(DictionaryWord, self).__init__(word.encode('utf-8'),
                                             is_noun, is_verb,
                                             is_prep, is_meta,
                                             is_plural, is_dir,
                                             is_adj, is_special)

    def __repr__(self):
        return self.word

    @property
    def word(self):
        return self._word.decode('cp1252')

    def pos(self):
        pos = []
        if self.is_noun:
            pos.append('noun')
        if self.is_verb:
            pos.append('verb')
        if self.is_prep:
            pos.append('prep')
        if self.is_meta:
            pos.append('meta')
        if self.is_plural:
            pos.append('plural')
        if self.is_dir:
            pos.append('dir')
        if self.is_adj:
            pos.append('adj')
        if self.is_special:
            pos.append('special')
        return pos


def _load_frotz_lib():
    """ Loads a copy of frotz's shared library. """

    # Make a copy of libfrotz.so before loading it to avoid concurrency issues.
    with tempfile.TemporaryDirectory() as tmpdir:
        frotz_lib_path = os.path.join(tmpdir, 'libfrotz.so')
        shutil.copyfile(FROTZ_LIB_PATH, frotz_lib_path)
        frotz_lib = cdll.LoadLibrary(frotz_lib_path)

    frotz_lib.setup.argtypes = [c_char_p, c_int, c_char_p, c_int]
    frotz_lib.setup.restype = c_char_p
    frotz_lib.shutdown.argtypes = []
    frotz_lib.shutdown.restype = None
    frotz_lib.step.argtypes = [c_char_p]
    frotz_lib.step.restype = c_char_p
    frotz_lib.save.argtypes = [c_char_p]
    frotz_lib.save.restype = int
    frotz_lib.restore.argtypes = [c_char_p]
    frotz_lib.restore.restype = int
    frotz_lib.get_object.argtypes = [c_void_p, c_int]
    frotz_lib.get_object.restype = None
    frotz_lib.get_num_world_objs.argtypes = []
    frotz_lib.get_num_world_objs.restype = int
    frotz_lib.get_world_objects.argtypes = [POINTER(ZObject), c_int]
    frotz_lib.get_world_objects.restype = None
    frotz_lib.get_self_object_num.argtypes = []
    frotz_lib.get_self_object_num.restype = int
    frotz_lib.get_moves.argtypes = []
    frotz_lib.get_moves.restype = int
    frotz_lib.get_score.argtypes = []
    frotz_lib.get_score.restype = c_short
    frotz_lib.get_max_score.argtypes = []
    frotz_lib.get_max_score.restype = int
    frotz_lib.save_str.argtypes = [c_void_p]
    frotz_lib.save_str.restype = int
    frotz_lib.restore_str.argtypes = [c_void_p]
    frotz_lib.restore_str.restype = int
    frotz_lib.world_changed.argtypes = []
    frotz_lib.world_changed.restype = int
    frotz_lib.get_cleaned_world_diff.argtypes = [c_void_p, c_void_p]
    frotz_lib.get_cleaned_world_diff.restype = None
    frotz_lib.game_over.argtypes = []
    frotz_lib.game_over.restype = int
    frotz_lib.victory.argtypes = []
    frotz_lib.victory.restype = int
    frotz_lib.halted.argtypes = []
    frotz_lib.halted.restype = int

    frotz_lib.getRAMSize.argtypes = []
    frotz_lib.getRAMSize.restype = int
    frotz_lib.getRAM.argtypes = [c_void_p]
    frotz_lib.getRAM.restype = None

    frotz_lib.get_narrative_text.argtypes = []
    frotz_lib.get_narrative_text.restype = c_char_p
    frotz_lib.set_narrative_text.argtypes = [c_char_p]
    frotz_lib.set_narrative_text.restype = None

    frotz_lib.getPC.argtypes = []
    frotz_lib.getPC.restype = int
    frotz_lib.setPC.argtypes = [c_int]
    frotz_lib.setPC.restype = None

    frotz_lib.getSP.argtypes = []
    frotz_lib.getSP.restype = int
    frotz_lib.setSP.argtypes = [c_int]
    frotz_lib.setSP.restype = None

    frotz_lib.getFP.argtypes = []
    frotz_lib.getFP.restype = int
    frotz_lib.setFP.argtypes = [c_int]
    frotz_lib.setFP.restype = None

    frotz_lib.getFrameCount.argtypes = []
    frotz_lib.getFrameCount.restype = int
    frotz_lib.setFrameCount.argtypes = [c_int]
    frotz_lib.setFrameCount.restype = None

    frotz_lib.getRngA.argtypes = []
    frotz_lib.getRngA.restype = np.int64
    frotz_lib.getRngInterval.argtypes = []
    frotz_lib.getRngInterval.restype = int
    frotz_lib.getRngCounter.argtypes = []
    frotz_lib.getRngCounter.restype = int
    frotz_lib.setRng.argtypes = [c_long, c_int, c_int]
    frotz_lib.setRng.restype = None

    frotz_lib.getRAMSize.argtypes = []
    frotz_lib.getRAMSize.restype = int
    frotz_lib.getRAM.argtypes = [c_void_p]
    frotz_lib.getRAM.restype = None
    frotz_lib.setRAM.argtypes = [c_void_p]
    frotz_lib.setRAM.restype = None
    frotz_lib.getStack.argtypes = [c_void_p]
    frotz_lib.getStack.restype = None
    frotz_lib.setStack.argtypes = [c_void_p]
    frotz_lib.setStack.restype = None
    frotz_lib.getStackSize.argtypes = []
    frotz_lib.getStackSize.restype = int
    frotz_lib.disassemble.argtypes = [c_char_p]
    frotz_lib.disassemble.restype = None
    frotz_lib.is_supported.argtypes = [c_char_p]
    frotz_lib.is_supported.restype = int
    frotz_lib.get_dictionary_word_count.argtypes = [c_char_p]
    frotz_lib.get_dictionary_word_count.restype = int
    frotz_lib.get_dictionary.argtypes = [POINTER(DictionaryWord)]
    frotz_lib.get_dictionary.restype = None
    frotz_lib.ztools_cleanup.argtypes = []
    frotz_lib.ztools_cleanup.restype = None
    return frotz_lib


def _load_bindings(md5hash):
    """
    Loads information pertaining to the current game. Returns a dictionary
    with the following keys:

    - `name`: Name of the game. E.g. `zork1`
    - `rom`: Name of the file used to load the game. E.g. `zork1.z5`
    - `walkthrough`: A walkthrough for the game.
    - `seed`: Seed necessary to replicate the walkthrough.
    - `grammar`: List of action templates for the game.
    - `max_word_length`: Maximum number of characters per word recognized by the parser.

    :param rom: Path or name of rom to load.
    :type rom: string

    :returns: Dictionary containing game-specific bindings if it exists.
              Otherwise, an empty dictionary.

    :Example:

    >>> import jericho
    >>> bindings = jericho._load_bindings('zork1')
    {
      'name': 'zork1',
      'rom': 'zork1.z5',
      'seed': 12,
      'max_word_length': 6,
      'minimal_actions': 'Ulysses/wait/pray/inventory/go down/...',
      'grammar': 'again/g;answer/reply;back;barf/chomp/...',
      'walkthrough': 'N/N/U/Get egg/D/S/E/Open window/...'
    }

    .. note:: Walkthroughs are defined for only a few games.
    """
    return defines.BINDINGS_DICT.get(md5hash, {})


class UnsupportedGameWarning(UserWarning):
    pass


class FrotzEnv():
    """
    The Frotz Environment is a fast interface to Z-Machine games.

    :param story_file: Path to a Z-machine rom file (.z3/.z5/.z6/.z8).
    :param seed: Seed the random number generator used by the emulator.
                 Default: use walkthrough's seed if it exists,
                          otherwise use value of -1 which changes with time.
    :type story_file: path
    :type seed: int

    """
    def __init__(self, story_file, seed=None):
        self._cache = {}
        self.frotz_lib = _load_frotz_lib()
        self.load(story_file, seed)

    def __del__(self):
        if hasattr(self, 'frotz_lib'):
            self.frotz_lib.shutdown()
            dlclose_func(self.frotz_lib._handle)

    def load(self, story_file, seed=None):
        '''
        Loads a Z-Machine game.

        :param story_file: Path to a Z-machine rom file (.z3/.z5/.z6/.z8).
        :param seed: Seed the random number generator used by the emulator.
                    Default: use walkthrough's seed if it exists,
                            otherwise use value of -1 which changes with time.
        :type story_file: path
        :type seed: int
        '''
        self.story_file = story_file.encode('utf-8')

        if story_file not in self._cache:
            if not os.path.isfile(story_file):
                raise FileNotFoundError(story_file)

            with open(story_file, "rb") as f:
                rom = f.read()

            self.is_fully_supported = bool(self.frotz_lib.is_supported(self.story_file))
            if not self.is_fully_supported:
                msg = ("Game '{}' is not fully supported. Score, move, change"
                    " detection will be disabled.").format(story_file)
                warnings.warn(msg, UnsupportedGameWarning)

            md5hash = hashlib.md5(rom).hexdigest()
            self.bindings = _load_bindings(md5hash)
            self.act_gen = TemplateActionGenerator(self.bindings) if self.bindings else None

            self._cache[story_file] = (rom, self.bindings, self.act_gen)

        rom, self.bindings, self.act_gen = self._cache[story_file]

        self.seed(seed)
        self.frotz_lib.setup(self.story_file, self._seed, rom, len(rom))
        self.player_obj_num = self.frotz_lib.get_self_object_num()

    def seed(self, seed=None):
        '''
        Changes seed used for the emulator's random number generator.

        :param seed: Seed the random number generator used by the emulator.
                     Default: use walkthrough's seed if it exists,
                              otherwise use value of -1 which changes with time.
        :returns: The value of the seed.

        .. note:: :meth:`jericho.FrotzEnv.reset()` must be called before the seed takes effect.

        '''
        seed = seed or self.bindings.get('seed', -1)
        self._seed = seed
        return seed

    def reset(self):
        '''
        Resets the game.

        :param use_walkthrough_seed: Seed the emulator to reproduce the walkthrough.
        :returns: A tuple containing the initial observation,\
        and a dictionary of info.
        :rtype: string, dictionary

        '''
        self.close()
        rom, _, _ = self._cache[self.story_file.decode()]
        obs_ini = self.frotz_lib.setup(self.story_file, self._seed, rom, len(rom)).decode('cp1252')
        score = self.frotz_lib.get_score()
        return obs_ini, {'moves':self.get_moves(), 'score':score}

    def step(self, action):
        '''
        Takes an action and returns the next state, reward, termination

        :param action: Text command to send to the interpreter.
        :type action: string

        :returns: A tuple containing the game's textual response to the action,\
        the immediate reward, a boolean indicating whether the game is over,\
        and a dictionary of info.
        :rtype: string, float, boolean, dictionary
        '''
        old_score = self.frotz_lib.get_score()
        next_state = self.frotz_lib.step((action+'\n').encode('utf-8')).decode('cp1252')
        score = self.frotz_lib.get_score()
        reward = score - old_score
        return next_state, reward, (self.game_over() or self.victory()),\
            {'moves':self.get_moves(), 'score':score}

    def close(self):
        ''' Cleans up the FrotzEnv, freeing any allocated memory. '''
        self.frotz_lib.shutdown()

    def get_dictionary(self):
        ''' Returns a list of :class:`jericho.DictionaryWord` words recognized\
        by the game's parser. See :doc:`dictionary`. '''
        word_count = self.frotz_lib.get_dictionary_word_count(self.story_file)
        words = (DictionaryWord * word_count)()
        self.frotz_lib.get_dictionary(words, word_count)
        self.frotz_lib.ztools_cleanup()
        return list(words)

    def get_walkthrough(self):
        ''' Returns the walkthrough for the game.

        :returns: A list containing walkthrough action strings needed to complete the game.

        .. note:: To reproduce the walkthrough it's also necessary to reset the environment\
        with use_walkthrough_seed=True.
        '''
        if not self.is_fully_supported or not self.bindings:
            warnings.warn('Unable to retrieve walkthrough for this game.', UnsupportedGameWarning)
            return []
        return self.bindings['walkthrough'].split('/')

    def get_valid_actions(self, use_object_tree=True):
        """
        Attempts to generate a set of unique valid actions from the current game state.

        :param use_object_tree: Query the :doc:`object_tree` for names of surrounding objects.
        :type use_object_tree: boolean
        :returns: A list of valid actions.

        """
        if not self.is_fully_supported or not self.act_gen:
            warnings.warn('Unable to find valid actions in an unsupported game.', UnsupportedGameWarning)
            return []
        interactive_objs  = self._identify_interactive_objects(use_object_tree=use_object_tree)
        best_obj_names    = self._score_object_names(interactive_objs)
        candidate_actions = self.act_gen.generate_actions(best_obj_names)
        diff2acts         = self._filter_candidate_actions(candidate_actions)
        valid_actions     = [max(v, key=utl.verb_usage_count) for v in diff2acts.values()]
        return valid_actions

    def set_state(self, state):
        '''
        Sets the game's internal state.

        :param state: Tuple of (ram, stack, pc, sp, fp, frame_count, rng) as\
        obtained by :meth:`jericho.FrotzEnv.get_state`.
        :type state: tuple

        >>> from jericho import *
        >>> env = FrotzEnv(rom_path)
        >>> state = env.get_state()
        >>> env.step('attack troll') # Oops!
        'You swing and miss. The troll neatly removes your head.'
        >>> env.set_state(state) # Whew, let's try something else

        '''
        ram, stack, pc, sp, fp, frame_count, rng, narrative = state
        self.frotz_lib.setRng(*rng)
        self.frotz_lib.setRAM(as_ctypes(ram))
        self.frotz_lib.setStack(as_ctypes(stack))
        self.frotz_lib.setPC(pc)
        self.frotz_lib.setSP(sp)
        self.frotz_lib.setFP(fp)
        self.frotz_lib.setFrameCount(frame_count)
        self.frotz_lib.set_narrative_text(narrative)

    def get_state(self):
        '''
        Returns the internal game state. This state can be subsequently restored
        using :meth:`jericho.FrotzEnv.set_state`.

        :returns: Tuple of (ram, stack, pc, sp, fp, frame_count, rng).

        >>> from jericho import *
        >>> env = FrotzEnv(rom_path)
        >>> state = env.get_state()
        >>> env.step('attack troll') # Oops!
        'You swing and miss. The troll neatly removes your head.'
        >>> env.set_state(state) # Whew, let's try something else

        '''
        ram = np.zeros(self.frotz_lib.getRAMSize(), dtype=np.uint8)
        stack = np.zeros(self.frotz_lib.getStackSize(), dtype=np.uint8)
        self.frotz_lib.getRAM(as_ctypes(ram))
        self.frotz_lib.getStack(as_ctypes(stack))
        pc = self.frotz_lib.getPC()
        sp = self.frotz_lib.getSP()
        fp = self.frotz_lib.getFP()
        frame_count = self.frotz_lib.getFrameCount()
        rng = self.frotz_lib.getRngA(), self.frotz_lib.getRngInterval(), self.frotz_lib.getRngCounter()
        narrative = self.frotz_lib.get_narrative_text()
        state = ram, stack, pc, sp, fp, frame_count, rng, narrative
        return state

    def get_max_score(self):
        ''' Returns the integer maximum possible score for the game. '''
        return self.frotz_lib.get_max_score()

    def copy(self):
        ''' Forks this FrotzEnv instance. '''
        state = self.get_state()
        env = FrotzEnv(self.story_file.decode(), seed=self._seed)
        env.set_state(state)
        return env

    def get_player_location(self):
        ''' Returns the :class:`jericho.ZObject` corresponding to the location of the player in the world. '''
        parent = self.get_player_object().parent
        return self.get_object(parent)

    def get_object(self, obj_num):
        '''
        Returns a :class:`jericho.ZObject` with the corresponding number or `None` if the object\
        doesn't exist in the :doc:`object_tree`.

        :param obj_num: Object number between 0 and len(get_world_objects()).
        :type obj_num: int
        '''
        obj = ZObject()
        self.frotz_lib.get_object(byref(obj), obj_num)
        if obj.num < 0:
            return None
        return obj

    def get_world_objects(self, clean=False):
        ''' Returns an array containing all the :class:`jericho.ZObject` in the game.

        :param clean: If True, disconnects noisy objects like Zork1's theif from\
        the Object Tree. This is mainly useful if using world objects as an\
        indication of unique game state.
        :type clean: Boolean

        :returns: Array of :class:`jericho.ZObject`.

        :Example:

        >>> from jericho import *
        >>> env = FrotzEnv('zork1.z5')
        >>> env.get_world_objects()
         Obj0:  Parent0 Sibling0 Child0 Attributes [] Properties [],
         Obj1: pair hands Parent247 Sibling2 Child0 Attributes [14, 28] Properties [18, 16],
         Obj2: zorkmid Parent247 Sibling3 Child0 Attributes [] Properties [18, 17],
         Obj3: way Parent247 Sibling5 Child0 Attributes [14] Properties [18, 17, 16],
         Obj4: cretin Parent180 Sibling181 Child0 Attributes [7, 9, 14, 30] Properties [18, 17, 7],
         Obj5: you Parent247 Sibling6 Child0 Attributes [30] Properties [18, 17],
         ...
         Obj250: board Parent249 Sibling73 Child0 Attributes [14] Properties [18, 17]

        '''
        n_objs = self.frotz_lib.get_num_world_objs()
        objs = (ZObject * (n_objs+1))() # Add extra spot for zero'th object
        self.frotz_lib.get_world_objects(objs, clean)
        return objs

    def get_player_object(self):
        ''' Returns the :class:`jericho.ZObject` corresponding to the player. '''
        return self.get_object(self.player_obj_num)

    def get_inventory(self):
        ''' Returns a list of :class:`jericho.ZObject` in the player's posession. '''
        inventory = []
        item_nb = self.get_player_object().child
        while item_nb > 0:
            item = self.get_object(item_nb)
            if not item:
                break
            inventory.append(item)
            item_nb = item.sibling
        return inventory

    def get_world_state_hash(self):
        """ Returns a MD5 hash of the clean world-object-tree. Such a hash may be
        useful for identifying when the agent has reached new states or returned
        to existing ones.

        :Example:

        >>> env = FrotzEnv('zork1.z5')
        >>> env.reset()
        # Start at West of the House with the following hash
        >>> env.get_world_state_hash()
        '79c750fff4368efef349b02ff50ffc23'
        >>> env.step('n')
        # Moving to North of House changes the hash
        >>> get_world_state_hash(env)
        '8a3a8538c0019a69128f755e4b719fbd'
        >>> env.step('w')
        # Moving back to West of House we recover the original hash
        >>> env.get_world_state_hash()
        '79c750fff4368efef349b02ff50ffc23'

        """
        import hashlib
        world_str = ', '.join([str(o) for o in self.get_world_objects(clean=True)])
        m = hashlib.md5()
        m.update(world_str.encode('utf-8'))
        return m.hexdigest()

    def get_moves(self):
        ''' Returns the integer number of moves taken by the player in the current episode. '''
        return self.frotz_lib.get_moves()

    def get_score(self):
        ''' Returns the integer current game score. '''
        return self.frotz_lib.get_score()

    def victory(self):
        ''' Returns `True` if the game is over and the player has won. '''
        return self.frotz_lib.victory() > 0

    def game_over(self):
        ''' Returns `True` if the game is over and the player has lost. '''
        return self.frotz_lib.game_over() > 0

    def _disassemble_game(self):
        ''' Prints the subroutines and strings used by the game. '''
        self.frotz_lib.disassemble(self.story_file)

    def _emulator_halted(self):
        ''' Returns `True` if the emulator has halted. To fix a halted game, use :meth:`jericho.FrotzEnv.reset`. '''
        return self.frotz_lib.halted() > 0

    def _world_changed(self):
        ''' Returns True if the last action caused a change in the world.

        :Example:

        >>> from jericho import *
        >>> env = FrotzEnv('zork1.z5')
        >>> env.step('north')[0]
        'North of House You are facing the north side of a white house.'
        >>> env.world_changed()
        True
        >>> env.step('south')[0]
        'The windows are all boarded.'
        >>> env.world_changed()
        False
        '''
        return self.frotz_lib.world_changed() > 0

    def _get_world_diff(self):
        '''
        Returns the difference in the world object tree, set attributes, and\
        cleared attributes for the last timestep.

        :returns: A Tuple of tuples containing 1) tuple of world objects that \
        have moved in the Object Tree, 2) tuple of objects whose attributes have\
        changed, 3) tuple of world objects whose attributes have been cleared, and
        4) tuple of special ram locations whose values have changed.
        '''
        objs = np.zeros(64, dtype=np.uint16)
        dest = np.zeros(64, dtype=np.uint16)
        self.frotz_lib.get_cleaned_world_diff(as_ctypes(objs), as_ctypes(dest))
        # First 16 spots allocated for objects that have moved
        moved_objs = []
        for i in range(16):
            if objs[i] == 0 or dest[i] == 0:
                break
            moved_objs.append((objs[i], dest[i]))
        # Second 16 spots allocated for objects that have had attrs set
        set_attrs = []
        for i in range(16, 32):
            if objs[i] == 0 or dest[i] == 0:
                break
            set_attrs.append((objs[i], dest[i]))
        # Third 16 spots allocated for objects that have had attrs cleared
        cleared_attrs = []
        for i in range(32, 48):
            if objs[i] == 0 or dest[i] == 0:
                break
            cleared_attrs.append((objs[i], dest[i]))
        # Fourth 16 spots allocated to ram locations & values that have changed
        ram_diffs = []
        for i in range(48, 64):
            if objs[i] == 0:
                break
            ram_diffs.append((objs[i], dest[i]))
        return (tuple(moved_objs), tuple(set_attrs), tuple(cleared_attrs), tuple(ram_diffs))

    def _score_object_names(self, interactive_objs):
        """ Attempts to choose a sensible name for an object, typically a noun. """
        def score_fn(obj):
            score = -.01 * len(obj[0])
            if obj[1] == 'NOUN':
                score += 1
            if obj[1] == 'PROPN':
                score += .5
            if obj[1] == 'ADJ':
                score += 0
            if obj[2] == 'OBJTREE':
                score += .1
            return score
        best_names = []
        for desc, objs in interactive_objs.items():
            sorted_objs = sorted(objs, key=score_fn, reverse=True)
            best_names.append(sorted_objs[0][0])
        return best_names

    def _identify_interactive_objects(self, observation='', use_object_tree=False):
        """
        Identifies objects in the current location and inventory that are likely
        to be interactive.

        :param observation: (optional) narrative response to the last action, used to extract candidate objects.
        :type observation: string
        :param use_object_tree: Query the :doc:`object_tree` for names of surrounding objects.
        :type use_object_tree: boolean
        :returns: A list-of-lists containing the name(s) for each interactive object.

        :Example:

        >>> from jericho import *
        >>> env = FrotzEnv('zork1.z5')
        >>> obs, info = env.reset()
        'You are standing in an open field west of a white house with a boarded front door. There is a small mailbox here.'
        >>> env.identify_interactive_objects(obs)
        [['mailbox', 'small'], ['boarded', 'front', 'door'], ['white', 'house']]

        .. note:: Many objects may be referred to in a variety of ways, such as\
        Zork1's brass latern which may be referred to either as *brass* or *lantern*.\
        This method groups all such aliases together into a list for each object.
        """
        objs = set()
        state = self.get_state()

        if observation:
            # Extract objects from observation
            obs_objs = utl.extract_objs(observation)
            obs_objs = [o + ('OBS',) for o in obs_objs]
            objs = objs.union(obs_objs)

        # Extract objects from location description
        self.set_state(state)
        look = utl.clean(self.step('look')[0])
        look_objs = utl.extract_objs(look)
        look_objs = [o + ('LOC',) for o in look_objs]
        objs = objs.union(look_objs)

        # Extract objects from inventory description
        self.set_state(state)
        inv = utl.clean(self.step('inventory')[0])
        inv_objs = utl.extract_objs(inv)
        inv_objs = [o + ('INV',) for o in inv_objs]
        objs = objs.union(inv_objs)
        self.set_state(state)

        # Optionally extract objs from the global object tree
        if use_object_tree:
            surrounding = utl.get_subtree(self.get_player_location().child, self.get_world_objects())
            player_obj = self.get_player_object()
            if player_obj in surrounding:
                surrounding.remove(player_obj)
            world_objs = []
            for o in surrounding:
                name = o.name.split()
                world_objs.append((o.name, 'PROPN', 'OBJTREE'))
                if len(name) > 1:
                    # In the case of multi-word names, we assume first words are adjectives.
                    for w in name[:-1]:
                        world_objs.append((w, 'ADJ', 'OBJTREE'))
                    world_objs.append((name[-1], 'NOUN', 'OBJTREE'))
            objs = objs.union(world_objs)

        # Filter out the objects that aren't in the dictionary
        dict_words = [w.word for w in self.get_dictionary()]
        max_word_length = max([len(w) for w in dict_words])
        to_remove = set()
        for obj in objs:
            if len(obj[0].split()) > 1:
                continue
            if obj[0][:max_word_length] not in dict_words:
                to_remove.add(obj)
        objs.difference_update(to_remove)

        desc2obj = {}
        # Filter out objs that aren't examinable
        name2desc = {}
        for obj in objs:
            if obj[0] in name2desc:
                ex = name2desc[obj[0]]
            else:
                self.set_state(state)
                ex = utl.clean(self.step('examine ' + obj[0])[0])
                name2desc[obj[0]] = ex
            if utl.recognized(ex):
                if ex in desc2obj:
                    desc2obj[ex].append(obj)
                else:
                    desc2obj[ex] = [obj]
        # Add 'all' as a wildcard object
        desc2obj['all'] = [('all', 'NOUN', 'LOC')]
        self.set_state(state)
        return desc2obj

    def _filter_candidate_actions(self, candidate_actions):
        """
        Given a list of candidate actions, returns a dictionary mapping world_diff
        to the list of candidate actions that cause this diff. Only actions that
        cause a valid world diff are returned.

        :param candidate_actions: Candidate actions to test for validity.
        :type candidate_actions: list
        :returns: Dictionary of world_diff to list of actions.

        """
        if self.game_over() or self.victory() or self._emulator_halted():
            return {} 
        diff2acts = {}
        orig_score = self.get_score()
        state = self.get_state()
        for act in candidate_actions:
            self.set_state(state)
            if isinstance(act, defines.TemplateAction):
                obs, rew, done, info = self.step(act.action)
            else:
                obs, rew, done, info = self.step(act)
            if self._emulator_halted():
                self.reset()
                continue
            if info['score'] != orig_score or done or self._world_changed():
                # Heuristic to ignore actions with side-effect of taking items
                if '(Taken)' in obs:
                    continue
                diff = self._get_world_diff()
                if diff in diff2acts:
                    if act not in diff2acts[diff]:
                        diff2acts[diff].append(act)
                else:
                    diff2acts[diff] = [act]
        self.set_state(state)
        return diff2acts

    def _get_ram(self):
        """
        Returns a numpy array containing the contents of the Z-Machine's RAM.

        """
        ram_size = self.frotz_lib.getRAMSize()
        ram = np.zeros(ram_size, dtype=np.uint8)
        self.frotz_lib.getRAM(as_ctypes(ram))
        return ram
