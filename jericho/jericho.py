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
    """ A Z-Machine Object contains the following fields: More info:
    http://inform-fiction.org/zmachine/standards/z1point1/sect12.html

    num: Object number
    name: Short object name
    parent: Object number of parent
    sibling: Object number of sibling
    child: Object number of child
    attr: 32-bit array of object attributes
    properties: list of object properties

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
    A word contained in the dictionary of a game.

    word: Value of the word.
    is_*: Boolean indicating accepted parts of speech for this word.
    is_meta: Used for meta commands like 'verbose' and 'script'
    is_plural: Used for pluralized nouns (e.g. bookcases, rooms)
    is_dir: Used for direction words (e.g. north, aft)
    is_special: Used for special commands like 'again' which repeats last action.

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
    """ FrotzEnv is a fast interface to the ZMachine. """

    def __init__(self, story_file, seed=-1):
        if not os.path.isfile(story_file):
            raise FileNotFoundError(story_file)

        if not self.is_fully_supported(story_file):
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
        # Returns a list of dictionary words for the game
        word_count = frotz_lib.get_dictionary_word_count(self.story_file)
        words = (DictionaryWord * word_count)()
        frotz_lib.get_dictionary(words, word_count)
        return list(words)

    def disassemble_game(self):
        # Prints the routines and strings used by the game
        frotz_lib.disassemble(self.story_file)

    def victory(self):
        # Returns true if the last step caused the game to be won
        return frotz_lib.victory() > 0

    def game_over(self):
        # Returns true if the last step caused the game to be over (lost)
        return frotz_lib.game_over() > 0

    def emulator_halted(self):
        # Returns true if the emulator has halted due to a runtime error
        return frotz_lib.halted() > 0

    def step(self, action):
        # Takes an action and returns the next state, total score
        next_state = frotz_lib.step((action+'\n').encode('utf-8')).decode('cp1252')
        return next_state, frotz_lib.get_score(), (self.game_over() or self.victory()),\
            {'moves':self.get_moves()}

    def world_changed(self):
        # Returns true if the last action caused a change in the world
        return frotz_lib.world_changed() > 0

    def close(self):
        frotz_lib.shutdown()

    def reset(self):
        # Resets the game and returns the initial state
        self.close()
        return frotz_lib.setup(self.story_file, self.seed).decode('cp1252')

    def save(self, fname):
        # Save the game to file. Prefer save_str() for efficiency.
        success = frotz_lib.save(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to save.')

    def load(self, fname):
        # Restore the game from a save file. Prefer load_str() for efficiency.
        success = frotz_lib.restore(fname.encode('utf-8'))
        if success <= 0:
            raise RuntimeError('Unable to load.')

    def save_str(self):
        # Saves the game and returns a string containing the saved game
        buff = np.zeros(8192, dtype=np.uint8)
        success = frotz_lib.save_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to save.')
        return buff

    def load_str(self, buff):
        # Load the game from a string buffer given by save_str()
        success = frotz_lib.restore_str(as_ctypes(buff))
        if success <= 0:
            raise RuntimeError('Unable to load.')

    def get_player_location(self):
        # Returns the object corresponding to the location of the player in the world
        parent = self.get_player_object().parent
        return self.get_object(parent)

    def get_object(self, obj_num):
        # Returns an ZObject with the corresponding number or None if
        # the object doesn't exist.
        obj = ZObject()
        frotz_lib.get_object(byref(obj), obj_num)
        if obj.num < 0:
            return None
        return obj

    def get_world_objects(self, clean=False):
        # Returns an array containing all the zobjects in the game. If
        # clean is True, then noisy objects like Zork1's thief will be
        # disconnected, allowing the representation to be used as an
        # indication of the game state from the player's perspective.
        n_objs = frotz_lib.get_num_world_objs()
        objs = (ZObject * (n_objs+1))() # Add extra spot for zero'th object
        frotz_lib.get_world_objects(objs, clean)
        return objs

    def get_player_object(self):
        # Returns the object corresponding to the player
        return self.get_object(self.player_obj_num)

    def get_inventory(self):
        # Returns a list of objects in the player's posession.
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
        # Returns the number of moves taken
        return frotz_lib.get_moves()

    def get_score(self):
        # Returns the score for the current game
        return frotz_lib.get_score()

    def get_max_score(self):
        # Returns the maximum possible score for the game
        return frotz_lib.get_max_score()

    def get_world_diff(self):
        # Gets the difference in world objects, set attributes, and
        # cleared attributes for the last timestep.
        # Returns three tuples of (obj_nb, dest):
        #   moved_objs:    Tuple of moved objects (obj_nb, obj_destination)
        #   set_attrs:     Tuple of objects with attrs set: (obj_nb, attr_nb)
        #   cleared_attrs: Tuple of objects with attrs cleared: (obj_nb, attr_nb)
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


    def get_ram(self):
        # Returns the contents of the ZMachine's RAM
        ram_size = frotz_lib.getRAMSize()
        ram = np.zeros(ram_size, dtype=np.uint8)
        frotz_lib.getRAM(as_ctypes(ram))
        return ram

    @classmethod
    def is_fully_supported(cls, story_file):
        # Returns true if the story_file is amongst the supported games
        return bool(frotz_lib.is_supported(story_file.encode('utf-8')))
