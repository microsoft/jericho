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

#: Dictionary mapping game name to bindings for that game
BINDINGS_DICT = {
    '905'           : nine05,
    'nine05'        : nine05,
    'acorncourt'    : acorncourt,
    'adventureland' : adventureland,
    'advent'        : advent,
    'afflicted'     : afflicted,
    'anchorhead'    : anchorhead,
    'anchor'        : anchorhead,
    'awaken'        : awaken,
    'balances'      : balances,
    'ballyhoo'      : ballyhoo,
    'curses'        : curses,
    'cutthroat'     : cutthroat,
    'deephome'      : deephome,
    'detective'     : detective,
    'dragon'        : dragon,
    'enchanter'     : enchanter,
    'enter'         : enter,
    'gold'          : gold,
    'hhgg'          : hhgg,
    'hollywood'     : hollywood,
    'huntdark'      : huntdark,
    'infidel'       : infidel,
    'inhumane'      : inhumane,
    'jewel'         : jewel,
    'karn'          : karn,
    'library'       : library,
    'loose'         : loose,
    'lostpig'       : lostpig,
    'ludicorp'      : ludicorp,
    'lurking'       : lurking,
    'moonlit'       : moonlit,
    'murdac'        : murdac,
    'night'         : night,
    'omniquest'     : omniquest,
    'partyfoul'     : partyfoul,
    'pentari'       : pentari,
    'planetfall'    : planetfall,
    'plundered'     : plundered,
    'reverb'        : reverb,
    'seastalker'    : seastalker,
    'sherbet'       : sherbet,
    'sherlock'      : sherlock,
    'snacktime'     : snacktime,
    'sorcerer'      : sorcerer,
    'spellbrkr'     : spellbrkr,
    'spirit'        : spirit,
    'temple'        : temple,
    'theatre'       : theatre,
    'trinity'       : trinity,
    'tryst'         : tryst,
    'tryst205'      : tryst,
    'weapon'        : weapon,
    'wishbringer'   : wishbringer,
    'yomomma'       : yomomma,
    'zenon'         : zenon,
    'zork1'         : zork1,
    'zork2'         : zork2,
    'zork3'         : zork3,
    'ztuu'          : ztuu
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
