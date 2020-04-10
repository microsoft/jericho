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

import collections
import re
from .game_info import *

#: List of illegal actions that manipulate game state.
ILLEGAL_ACTIONS = 'license/licence/lisense/lisence/copyright/terms/eula/info/tutorial/changes/daemons/messages/actions/normal/win/lose/quotes/replay/recording/hint/menu/walkthru/walkthrou/manual/purloin/trace/about/clue/nouns/places/objects/long/short/notify/short/long/die/noscript/full/fullscore/credit/credits/help/super/save/versio/verbos/brief/restar/restor/again/$ve/verify/version/verbose/transcrip/tw-print/showme/showverb/showheap/superbrie/script/restore/restart/quit/q/random/responses/max_scor/fullscore/score/endofobje/comma,/./,/unscri/gonear'.split('/')

#: List of basic actions applicable to almost any game.
BASIC_ACTIONS = 'north/south/west/east/northwest/southwest/northeast/southeast/up/down/enter/exit/take all'.split('/')

#: List of actions that usually don't change the world state.
NO_EFFECT_ACTIONS = 'examine/x/look/l/i/inventory/gaze'.split('/')

unrecognized = [
    ".*That's not a verb I recognise.*",
    ".*I don't know the word \"(\w+)\.?\".*",
    ".*You used the word \"(\w+)\" in a way that I don't understand.*",
    ".*You can't see any \"?(.*)\"? here!*",
    ".*This story doesn't know the word \"(\w+)\.?\".*",
    ".*This story doesn't recognize the word \"(\w+)\.?\".*",
    ".*The word \"(\w+)\" isn't in the vocabulary that you can use.*",
    ".*You don't need to use the word \"(\w+)\" to finish this story.*",
    ".*You don't need to use the word \"(\w+)\" to complete this story.*",
    ".*Sorry, but the word \"(\w+)\" is not in the vocabulary you can use.*",
    ".*Sorry, but this story doesn't recognize the word \"(\w+)\.?\".*",
    ".*It's not clear what you're referring to..*",
    ".*There seems to be a noun missing in that sentence!.*",
    ".*That sentence isn't one I recognize.*",
    ".*What do you want to examine?.*",
    ".*You can't see any such thing.*",
    ".*That's not something you need to refer to in the course of this game.*"
]

#: List of regular expressions meant to capture game responses that indicate the
#: last action was unrecognized. This list covers most common paterns. However,
#: some games like `loose.z5` and `lostpig.z8` write custom responses that may note
#: be captured.
UNRECOGNIZED_REGEXPS = [re.compile(regexp) for regexp in unrecognized]

#: The action abbreviation dictionary contains abbreviations of common actions.
ABBRV_DICT = {
    'n' : 'north',
    's' : 'south',
    'w' : 'west',
    'e' : 'east',
    'd' : 'down',
    'u' : 'up',
    'g' : 'again',
    'l' : 'look',
    'i' : 'inventory',
    'z' : 'wait',
    'y' : 'yes',
    'x' : 'examine',
    'q' : 'quit',
    't' : 'talk',
    'ne' : 'northeast',
    'nw' : 'northwest',
    'se' : 'southeast',
    'sw' : 'southwest'
}

#: Dictionary mapping game's md5 hash to bindings for that game
BINDINGS_DICT = {
    '4c5067169b834d247a30bb08d1039896' : nine05,
    'a61400439aa76f8faba3b8f01edd4a72' : acorncourt,
    'a42545bd17330ae5e6fed02270ccfb4a' : adventureland,
    'ee2242e155fd8910921b0f8e04019a3a' : advent,
    '064272be87de7106192b6fb743c4dfc4' : afflicted,
    'c043df8624e0e1e9fda92f1a74b6e402' : anchorhead,
    '9ba48c72d96ab3e7956a8570b12d34d6' : awaken,
    'f2cb8f94a7e8df3b850a758da26fa387' : balances,
    '5d54e326815b0ed3aff8efb8ff02ef2f' : ballyhoo,
    'f06a42a29a5a4e6aa70958c9ae4c37cd' : curses,
    '216eeeba1c8017a77343dc8482f6f185' : cutthroat,
    '5e56a6e5cdeecded434a8fd8012fc2c6' : deephome,
    '822655c9be83e292e06d3d3b1d6a9734' : detective,
    '96d314997e5d3a5a793c83845977d44d' : dragon,
    'ad3cdea88d81033fe29167688bd98c31' : enchanter,
    '4c48ba2c5523d78c5f7f9b7809d16b1d' : enter,
    'f275ddf32ce8a9e744d53c3b99c5a658' : gold,
    '6666389f60e0c8e4ceb08242a263bb52' : hhgg,
    '1ea91a064941a3f612b20833f0a47df7' : hollywood,
    '253b02c8012710577085b9fd3a155cb7' : huntdark,
    '425fa66869309d7ed7f8ef04a492fbb7' : infidel,
    '84d3ce7ccfafb873736490811a0cc78c' : inhumane,
    '1eef9c0fa009ca4adf4872cfc5249d45' : jewel,
    'ec55791be814db3663ad1aec0d6b7690' : karn,
    'daf57133d346442b983bd333fb586cc4' : library,
    '31a0c1e360dce94aa5bece5240691d17' : loose,
    'aaf0b90fbb31717481c02832bf412070' : lostpig,
    '646a63307f77dcdcd011f330277ae262' : ludicorp,
    '5f42ff092a2f30471ae98150ef4da2e1' : lurking,
    'bf75b9651cff0e2d04302f19c443588e' : moonlit,
    '570179d4f21b2f600862dbffbb5afc3e' : murdac,
    '72125f159cccd581786ac16a2828d4e3' : night,
    '80ea198bca425b6d819c74bfa854236e' : omniquest,
    'd221daa82708c4e54447f1a884c239ef' : partyfoul,
    'f24c6863468823b744e910ccfe997c6d' : pentari,
    '6487dc814b280f5603c53155de378d27' : planetfall,
    '6ae4fd54b7e55675ec7e54ec4dd26462' : plundered,
    'be6d5fa9587a079782b64739e629461f' : reverb,
    'ee339dbdbb0792f67e20bd71bafe0ea5' : seastalker,
    '53bf7a60017e06998cc1542cf35f76fa' : sherbet,
    '35240654d83f9e7073973d338f9657b8' : sherlock,
    '0ff228d12d7cb470dc1a8e9a5151769b' : snacktime,
    '20f1468a058d0a6de016ae70022e651c' : sorcerer,
    '7a92ce19a39bedd970d0f1e296981f71' : spellbrkr,
    '808039c4e9554bdd15d7793539b3bd97' : spirit,
    '22a0ddac6be15540616c10f1007197f3' : temple,
    '33dcc5085acb290d1817e07653c13480' : theatre,
    '3bf1a444a1fc2057130ecb9806117233' : trinity,
    'fc65ad8d4588da92fd39871f6f7463db' : tryst,
    'c632204be3849d6c5bb6f4eb5aca3cc0' : weapon,
    '87ed53d854f7e57c36106fca3b9cf5a6' : wishbringer,
    '5b10162a7a134e7b4c381ecedfb4bc44' : yomomma,
    '631cc926b4251f5a5f646d3a6bdac8c6' : zenon,
    'b732a93a6244ddd92a9b9a3e3a46c687' : zork1,
    '5bcd91ee055e9bd42812617571be227b' : zork2,
    'ffda9ee2d428fa2fa8e75a1914ff6959' : zork3,
    'd8e1578470cbc676e013e03d72c93141' : ztuu
}


TemplateAction = collections.namedtuple('TemplateAction', 'action, template_id, obj_ids')
'''
A TemplateAction provides a class to bundle a textual action with the
`template_id` and `object_ids` that generated the action.

:param action: The action text.
:type action: string
:param template_id: The numerical index of the template used to generate the action.
:type template_id: int
:param obj_ids: List of vocabulary ids used to fill in the template.
:type obj_ids: list
'''
