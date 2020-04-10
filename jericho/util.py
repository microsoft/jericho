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
from . import defines


def clean(s):
    """ Cleans a string for compact output.

    :Example:

    >>> clean(\'*This string\\nneeds a good clean.--\\n\\n*\')
    \'This string needs a good clean.\'

    """
    garbage_chars = ['\n', '*', '-']
    for c in garbage_chars:
        s = s.replace(c, ' ')
    return s.strip()


def _load_spacy():
    """ Loads spacy into the global namespace. """
    if 'spacy_nlp' not in globals():
        import spacy
        try:
            global spacy_nlp
            import en_core_web_sm
            spacy_nlp = en_core_web_sm.load()
        except Exception as e:
            print("Failed to load \'en\' with exception {}. Try: python -m spacy download en_core_web_sm".format(e))
            raise


def tokenize(str):
    """ Returns a list of tokens in a string (using Spacy).

    :Example:

    >>> tokenize('This is an example sentence.')
    ['this', 'is', 'an', 'example', 'sentence', '.']


    """
    _load_spacy()
    doc = spacy_nlp(str)
    return [word.lower_ for word in doc]


def unabbreviate(action):
    """ Returns an unabbreviated version of a text action.

    :Example:

    >>> unabbreviate('nw')
    'northwest'
    >>> unabbreviate('x sewer')
    'examine sewer'

    """
    unabbrv = []
    for w in action.strip().lower().split():
        if w in defines.ABBRV_DICT:
            unabbrv.append(defines.ABBRV_DICT[w])
        else:
            unabbrv.append(w)
    return ' '.join(unabbrv)


def recognized(response):
    """ Returns `True` if the game's response indicates the last
    action was successfully parsed.

    :param response: The game's textual response to the last action.
    :type response: string

    :Example:

    >>> recognized(\'I dont know the word \"Azerbijan\".\')
    False
    >>> recognized(\'The vines block your way.\')
    True

    .. note:: Invalid actions may often be recognzied. Only ungrammatical\
    actions are detected by this method.
    """
    for p in defines.UNRECOGNIZED_REGEXPS:
        match = p.match(response)
        if match:
            return False
    return True


def extract_objs(text):
    """
    Uses Spacy to extract a set of tokens corresponding to possible objects in the provided text.

    :Example:

    >>> extract_objs('The quick brown fox jumped over the lazy dog.')
    {\'brown\', \'dog\', \'fox\', \'lazy\', \'quick\'}

    .. note:: Returns adjectives as well as nouns since many games allow players\
    to refer to objects using adjectives.

    """
    _load_spacy()
    doc = spacy_nlp(text)
    s = set()
    for token in doc:
        if token.pos_ == 'ADJ':
            s.add((token.text.lower(), 'ADJ'))
        elif token.pos_ == 'NOUN' or token.pos_ == 'PROPN':
            s.add((token.text.lower(), 'NOUN'))
    return s


def get_subtree(obj_nb, full_object_tree):
    """
    Traverses the object tree, returning a list containing full subtree at obj_nb.

    :param obj_nb: :class:`jericho.ZObject.num` corresponding to the root of the subtree to collect.
    :type obj_nb: int
    :param full_object_tree: Full list of objects as given by Jericho's get_world_objects().
    :type full_object_tree: list
    :returns: A list :class:`jericho.ZObject` of all descendents and siblings of obj_nb.

    :Example:

    >>> env = FrotzEnv('zork1.z5')
    >>> world_objs = env.get_world_objects()
    >>> env.get_player_object()
    Obj4: cretin Parent180 Sibling181 Child0 Attributes [7, 9, 14, 30] Properties [18, 17, 7]
    >>> get_subtree(4, world_objs)
    [
      Obj4: cretin Parent180 Sibling181 Child0 Attributes [7, 9, 14, 30] Properties [18, 17, 7],
      Obj181: door Parent180 Sibling160 Child0 Attributes [14, 23] Properties [18, 17, 16],
      Obj160: mailbox Parent180 Sibling0 Child161 Attributes [13, 19] Properties [18, 17, 16, 10],
      Obj161: leaflet Parent160 Sibling0 Child0 Attributes [16, 17, 26] Properties [18, 16, 15, 11, 8]
    ]

    """
    l = []
    if obj_nb > 0 and obj_nb < len(full_object_tree):
        obj = full_object_tree[obj_nb]
        l.append(obj)
        if obj.child != obj_nb:
            l.extend(get_subtree(obj.child, full_object_tree))
        if obj.sibling != obj_nb:
            l.extend(get_subtree(obj.sibling, full_object_tree))
    return l


def verb_usage_count(verb, max_word_length=None):
    """
    Returns the number of times that a particular verb appears across all
    clubfloyd transcripts.

    :params verb: Retrieve a usage count for this verb.
    :type verb: string

    :Example:

    >>> verb_usage_count('take')
    8909
    >>> verb_usage_count('jump')
    786

    """
    import json
    if isinstance(verb, defines.TemplateAction):
        verb = verb.action
    verb = verb.strip().lower()
    if len(verb.split()) > 0:
        verb = verb.split()[0]

    if 'clubfloyd_verb_counts' not in globals():
        dir_path = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(dir_path, 'clubfloyd_verb_counts.json'), 'r') as f:
            global clubfloyd_verb_counts
            clubfloyd_verb_counts = json.load(f)

    # Do a prefix check on any possibly prefixed verbs
    if max_word_length is not None and len(verb) == max_word_length:
        tot = 0
        for k,v in clubfloyd_verb_counts.items():
            if k.startswith(verb):
                tot += v
        return tot

    if verb in clubfloyd_verb_counts:
        return clubfloyd_verb_counts[verb]
    return 0
