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
from . import defines
from . import util as utl
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


def load_frotz_lib():
    """ Loads a copy of frotz's shared library. """

    # Make a copy of libfrotz.so before loading it to avoid concurrency issues.
    with tempfile.TemporaryDirectory() as tmpdir:
        frotz_lib_path = os.path.join(tmpdir, 'libfrotz.so')
        shutil.copyfile(FROTZ_LIB_PATH, frotz_lib_path)
        frotz_lib = cdll.LoadLibrary(frotz_lib_path)

    frotz_lib.setup.argtypes = [c_char_p, c_int]
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


def load_bindings(rom):
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

    :raises ValueError: When there are no bindings defined for the current ROM.

    :returns: Dictionary containing game-specific bindings.

    :Example:

    >>> import jericho
    >>> bindings = jericho.load_bindings('zork1')
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
    rom = os.path.basename(rom)
    for k, v in defines.BINDINGS_DICT.items():
        if k == rom or v['rom'] == rom:
            return v

    raise ValueError('No bindings available for rom {}'.format(rom))


class UnsupportedGameWarning(UserWarning):
    pass


class FrotzEnv():
    """
    The Frotz Environment is a fast interface to Z-Machine games.

    :param story_file: Path to a Z-machine rom file (.z3/.z5/.z6/.z8).
    :param seed: Seed the random number generator used by the emulator. Default value of -1 seeds to time.
    :type story_file: path
    :type seed: int

    """
    def __init__(self, story_file, seed=-1):
        if not os.path.isfile(story_file):
            raise FileNotFoundError(story_file)

        self.frotz_lib = load_frotz_lib()
        self.is_fully_supported = bool(self.frotz_lib.is_supported(story_file.encode('utf-8')))
        if not self.is_fully_supported:
            msg = ("Game '{}' is not fully supported. Score, move, change"
                   " detection will be disabled.").format(story_file)
            warnings.warn(msg, UnsupportedGameWarning)

        self.story_file = story_file.encode('utf-8')
        self.seed = seed
        self.frotz_lib.setup(self.story_file, self.seed)
        self.player_obj_num = self.frotz_lib.get_self_object_num()

    def __del__(self):
        if hasattr(self, 'frotz_lib'):
            self.frotz_lib.shutdown()
            dlclose_func(self.frotz_lib._handle)

    def get_dictionary(self):
        ''' Returns a list of :class:`jericho.DictionaryWord` words recognized\
        by the game's parser. See :doc:`dictionary`. '''
        word_count = self.frotz_lib.get_dictionary_word_count(self.story_file)
        words = (DictionaryWord * word_count)()
        self.frotz_lib.get_dictionary(words, word_count)
        self.frotz_lib.ztools_cleanup()
        return list(words)

    def disassemble_game(self):
        ''' Prints the subroutines and strings used by the game. '''
        self.frotz_lib.disassemble(self.story_file)

    def victory(self):
        ''' Returns `True` if the game is over and the player has won. '''
        return self.frotz_lib.victory() > 0

    def game_over(self):
        ''' Returns `True` if the game is over and the player has lost. '''
        return self.frotz_lib.game_over() > 0

    def emulator_halted(self):
        ''' Returns `True` if the emulator has halted. To fix a halted game, use :meth:`jericho.FrotzEnv.reset`. '''
        return self.frotz_lib.halted() > 0

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

    def world_changed(self):
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

    def close(self):
        ''' Cleans up the FrotzEnv, freeing any allocated memory. '''
        self.frotz_lib.shutdown()

    def reset(self):
        '''
        Resets the game.

        :returns: A tuple containing the initial observation,\
        and a dictionary of info.
        :rtype: string, dictionary

        '''
        self.close()
        obs_ini = self.frotz_lib.setup(self.story_file, self.seed).decode('cp1252')
        score = self.frotz_lib.get_score()
        return obs_ini, {'moves':self.get_moves(), 'score':score}

    def save(self, fname):
        '''
        Saves the game to a file.

        .. deprecated:: 2.3
           Use :meth:`jericho.FrotzEnv.get_state` instead.

        :param fname: Desired filename to save the game to.
        :type fname: path
        :raises RuntimeError: if unable to save.

        '''
        success = self.frotz_lib.save(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to save.')

    def load(self, fname):
        '''
        Restores the game from a file.

        .. deprecated:: 2.3
           Use :meth:`jericho.FrotzEnv.set_state` instead.

        :param fname: Desired filename to load the game from.
        :type fname: path
        :raises RuntimeError: if unable to load.
        '''
        success = self.frotz_lib.restore(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to load.')

    def save_str(self):
        '''
        Saves the game to a string.

        .. deprecated:: 2.3
           Use :meth:`jericho.FrotzEnv.get_state` instead.

        :returns: String containing saved game.
        :raises RuntimeError: if unable to save.

        :Example:

        >>> from jericho import *
        >>> env = FrotzEnv(rom_path)
        >>> try:
        >>>     save = env.save_str()
        >>> except RuntimeError:
        >>>     print('Skipping Save')

        '''
        warnings.warn('save_str is deprecated; use get_state instead.', DeprecationWarning)
        buff = np.zeros(8192, dtype=np.uint8)
        success = self.frotz_lib.save_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to save.')
        return buff

    def load_str(self, buff):
        '''
        Loads the game from a string buffer given by save_str()

        .. deprecated:: 2.3
           Use :meth:`jericho.FrotzEnv.set_state` instead.

        :param buff: Buffer to load the game from.
        :type buff: string
        :raises RuntimeError: if unable to load.

        >>> from jericho import *
        >>> env = FrotzEnv(rom_path)
        >>> try:
        >>>     save = env.save_str()
        >>>     env.step('attack troll') # Oops!
        'You swing and miss. The troll neatly removes your head.'
        >>>     env.load_str(save) # Whew, let's try something else
        >>> except RuntimeError:
        >>>     print('Skipping Save')

        '''
        warnings.warn('load_str is deprecated. Use set_state instead.', DeprecationWarning)
        success = self.frotz_lib.restore_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to load.')

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
        state = ram, stack, pc, sp, fp, frame_count, rng
        return state

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
        ram, stack, pc, sp, fp, frame_count, rng = state
        self.frotz_lib.setRng(*rng)
        self.frotz_lib.setRAM(as_ctypes(ram))
        self.frotz_lib.setStack(as_ctypes(stack))
        self.frotz_lib.setPC(pc)
        self.frotz_lib.setSP(sp)
        self.frotz_lib.setFP(fp)
        self.frotz_lib.setFrameCount(frame_count)

    def copy(self):
        ''' Forks this FrotzEnv instance. '''
        state = self.get_state()
        env = FrotzEnv(self.story_file.decode(), seed=self.seed)
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

    def get_moves(self):
        ''' Returns the integer number of moves taken by the player in the current episode. '''
        return self.frotz_lib.get_moves()

    def get_score(self):
        ''' Returns the integer current game score. '''
        return self.frotz_lib.get_score()

    def get_max_score(self):
        ''' Returns the integer maximum possible score for the game. '''
        return self.frotz_lib.get_max_score()

    def _get_world_diff(self):
        '''
        Returns the difference in the world object tree, set attributes, and\
        cleared attributes for the last timestep.

        :returns: A Tuple of tuples containing 1) tuple of world objects that \
        have moved in the Object Tree, 2) tuple of objects whose attributes have\
        changed, 3) tuple of world objects whose attributes have been cleared.
        '''
        objs = np.zeros(48, dtype=np.uint16)
        dest = np.zeros(48, dtype=np.uint16)
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
        return (tuple(moved_objs), tuple(set_attrs), tuple(cleared_attrs))

    def identify_interactive_objects(self, observation='', use_object_tree=False):
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
            objs = objs.union(obs_objs)

        # Extract objects from location description
        self.set_state(state)
        look = utl.clean(self.step('look')[0])
        look_objs = utl.extract_objs(look)
        objs = objs.union(look_objs)

        # Extract objects from inventory description
        self.set_state(state)
        inv = utl.clean(self.step('inventory')[0])
        inv_objs = utl.extract_objs(inv)
        objs = objs.union(inv_objs)
        self.set_state(state)

        # Optionally extract objs from the global object tree
        if use_object_tree:
            surrounding = utl.get_subtree(self.get_player_location().child, self.get_world_objects())
            player_obj = self.get_player_object()
            if player_obj in surrounding:
                surrounding.remove(player_obj)
            surrounding_objs = ' '.join([o.name for o in surrounding]).split()
            objs = objs.union(surrounding_objs)

        # Filter out the objects that aren't in the dictionary
        dict_words = [w.word for w in self.get_dictionary()]
        max_word_length = max([len(w) for w in dict_words])
        to_remove = set()
        for obj in objs:
            if obj[:max_word_length] not in dict_words:
                to_remove.add(obj)
        objs.difference_update(to_remove)

        desc2obj = {}
        # Filter out objs that aren't examinable
        for obj in objs:
            self.set_state(state)
            ex = self.step('examine ' + obj)[0]
            if utl.recognized(ex):
                if ex in desc2obj:
                    desc2obj[ex].append(obj)
                else:
                    desc2obj[ex] = [obj]
        self.set_state(state)

        return list(desc2obj.values())

    def find_valid_actions(self, candidate_actions):
        """
        Given a list of candidate actions, returns the subset that change
        the state of the game. Because many different actions may
        cause the same world change, this method returns the most
        commonly used action for each world change.

        :param candidate_actions: Candidate actions to test for validity.
        :type candidate_actions: list
        :returns: A list of the candidate actions found to be valid.

        :Example:

        >>> from jericho import *
        >>> env = FrotzEnv('zork1.z5')
        >>> env.find_valid_actions(['north', 'east', 'open mailbox', 'hail taxi'])
        ['north', 'open mailbox']

        """
        if self.game_over() or self.victory() or self.emulator_halted():
            return []
        diff2acts = {}
        orig_score = self.get_score()
        state = self.get_state()
        for act in candidate_actions:
            self.set_state(state)
            if isinstance(act, defines.TemplateAction):
                obs, rew, done, info = self.step(act.action)
            else:
                obs, rew, done, info = self.step(act)
            if self.emulator_halted():
                self.reset()
                continue
            if info['score'] != orig_score or done or self.world_changed():
                # Heuristic to ignore actions with side-effect of taking items
                if '(Taken)' in obs:
                    continue
                diff = self._get_world_diff()
                if diff in diff2acts:
                    if act not in diff2acts[diff]:
                        diff2acts[diff].append(act)
                else:
                    diff2acts[diff] = [act]
        valid_acts = [max(v, key=utl.verb_usage_count) for v in diff2acts.values()]
        self.set_state(state)
        return valid_acts

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
