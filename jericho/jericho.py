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
import warnings
import numpy as np
from ctypes import *
from numpy.ctypeslib import as_ctypes
from pkg_resources import Requirement, resource_filename

FROTZ_LIB_PATH = resource_filename(Requirement.parse('jericho'), 'jericho')

frotz_lib = cdll.LoadLibrary(os.path.join(FROTZ_LIB_PATH, 'libfrotz.so'))


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

    .. note:: Not all games specify the parts of speech for dictionary words.
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
frotz_lib.getRAMSize.argtypes = []
frotz_lib.getRAMSize.restype = int
frotz_lib.getRAM.argtypes = [c_void_p]
frotz_lib.getRAM.restype = None
frotz_lib.disassemble.argtypes = [c_char_p]
frotz_lib.disassemble.restype = None
frotz_lib.is_supported.argtypes = [c_char_p]
frotz_lib.is_supported.restype = int
frotz_lib.get_dictionary_word_count.argtypes = [c_char_p]
frotz_lib.get_dictionary_word_count.restype = int
frotz_lib.get_dictionary.argtypes = [POINTER(DictionaryWord)]
frotz_lib.get_dictionary.restype = None


class UnsupportedGameWarning(UserWarning):
    pass


class FrotzEnv():
    """
    The Frotz Environment is a fast interface to Z-Machine games.

    :param story_file: Path to a Z-machine rom file (.z3/.z5/.z6/.z8).
    :param seed: Seed the random number generator used by the emulator. Default seeds to time.
    :type story_file: path
    :type seed: int

    """
    def __init__(self, story_file, seed=-1):
        if not os.path.isfile(story_file):
            raise FileNotFoundError(story_file)

        if not bool(frotz_lib.is_supported(story_file.encode('utf-8'))):
            msg = ("Game '{}' is not fully supported. Score, move, change"
                   " detection will be disabled.").format(story_file)
            warnings.warn(msg, UnsupportedGameWarning)

        self.story_file = story_file.encode('utf-8')
        self.seed = seed
        frotz_lib.setup(self.story_file, self.seed)
        self.player_obj_num = frotz_lib.get_self_object_num()

    def __del__(self):
        frotz_lib.shutdown()

    def get_dictionary(self):
        ''' Returns a list of :class:`jericho.DictionaryWord` words recognized\
        by the game's parser. '''
        word_count = frotz_lib.get_dictionary_word_count(self.story_file)
        words = (DictionaryWord * word_count)()
        frotz_lib.get_dictionary(words, word_count)
        return list(words)

    def disassemble_game(self):
        ''' Prints the subroutines and strings used by the game. '''
        frotz_lib.disassemble(self.story_file)

    def victory(self):
        ''' Returns True if the game is over and the player has won. '''
        return frotz_lib.victory() > 0

    def game_over(self):
        ''' Returns True if the game is over and the player has lost. '''
        return frotz_lib.game_over() > 0

    def emulator_halted(self):
        ''' Returns True if the emulator has halted. To fix a halt, the emulator must be reset. '''
        return frotz_lib.halted() > 0

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
        old_score = frotz_lib.get_score()
        next_state = frotz_lib.step((action+'\n').encode('utf-8')).decode('cp1252')
        score = frotz_lib.get_score()
        reward = score - old_score
        return next_state, reward, (self.game_over() or self.victory()),\
            {'moves':self.get_moves(), 'score':score}

    def world_changed(self):
        ''' Returns True if the last action caused a change in the world. '''
        return frotz_lib.world_changed() > 0

    def close(self):
        ''' Cleans up the FrotzEnv, freeing any allocated memory. '''
        frotz_lib.shutdown()

    def reset(self):
        '''
        Resets the game.

        :returns: Textual observation for the initial game state.
        :rtype: string
        '''
        self.close()
        return frotz_lib.setup(self.story_file, self.seed).decode('cp1252')

    def save(self, fname):
        '''
        Saves the game to a file.

        :param fname: Desired filename to save the game to.
        :type fname: path
        :raises RuntimeError: if unable to save.
        '''
        success = frotz_lib.save(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to save.')

    def load(self, fname):
        '''
        Restores the game from a file.

        :param fname: Desired filename to load the game from.
        :type fname: path
        :raises RuntimeError: if unable to load.
        '''
        success = frotz_lib.restore(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to load.')

    def save_str(self):
        '''
        Saves the game to a string.

        :returns: String containing saved game.
        :raises RuntimeError: if unable to save.
        '''
        buff = np.zeros(8192, dtype=np.uint8)
        success = frotz_lib.save_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to save.')
        return buff

    def load_str(self, buff):
        '''
        Loads the game from a string buffer given by save_str()

        :param buff: Buffer to load the game from.
        :type buff: string
        :raises RuntimeError: if unable to load.
        '''
        success = frotz_lib.restore_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to load.')

    def get_player_location(self):
        ''' Returns the :class:`jericho.ZObject` corresponding to the location of the player in the world. '''
        parent = self.get_player_object().parent
        return self.get_object(parent)

    def get_object(self, obj_num):
        '''
        Returns a :class:`jericho.ZObject` with the corresponding number or `None` if the object\
        doesn't exist in the Object Tree.

        :param obj_num: Object number between 0 and len(get_world_objects()).
        :type obj_num: int
        '''
        obj = ZObject()
        frotz_lib.get_object(byref(obj), obj_num)
        if obj.num < 0:
            return None
        return obj

    def get_world_objects(self, clean=False):
        ''' Returns an array containing all the :class:`jericho.ZObject` in the game.

        :param clean: If True, disconnects noisy objects like Zork1's theif from\
        the Object Tree. This is mainly useful if using world objects as an\
        indication of unique game state.
        :type clean: Boolean

        :returns: Array of ZObjects.
        '''
        n_objs = frotz_lib.get_num_world_objs()
        objs = (ZObject * (n_objs+1))() # Add extra spot for zero'th object
        frotz_lib.get_world_objects(objs, clean)
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
        ''' Returns the number of moves taken by the player in the current episode. '''
        return frotz_lib.get_moves()

    def get_score(self):
        ''' Returns the game score accrued in the current episode. '''
        return frotz_lib.get_score()

    def get_max_score(self):
        ''' Returns the maximum possible score for the game. '''
        return frotz_lib.get_max_score()

    def get_world_diff(self):
        '''
        Returns the difference in the world object tree, set attributes, and\
        cleared attributes for the last timestep.


        :returns: A Tuple of tuples containing 1) tuple of world objects that \
        have moved in the Object Tree, 2) tuple of objects whose attributes have\
        changed, 3) tuple of world objects whose attributes have been cleared.
        '''
        objs = np.zeros(48, dtype=np.uint16)
        dest = np.zeros(48, dtype=np.uint16)
        frotz_lib.get_cleaned_world_diff(as_ctypes(objs), as_ctypes(dest))
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
