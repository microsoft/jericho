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

import re
from .util import verb_usage_count
from . import defines


class TemplateActionGenerator:
    '''
    Generates actions using the template-action-space.

    :param rom_bindings: Game-specific bindings from :meth:`jericho.FrotzEnv.load_bindings`.
    :type rom_bindings: Dictionary

    '''
    def __init__(self, rom_bindings):
        self.rom_bindings = rom_bindings
        grammar = rom_bindings['grammar'].split(';')
        max_word_length = rom_bindings['max_word_length']
        self.templates = self._preprocess_templates(grammar, max_word_length)
        self.templates.extend(defines.BASIC_ACTIONS)
        # Enchanter and Spellbreaker only recognize abbreviated directions
        if rom_bindings['name'] in ['enchanter', 'spellbrkr']:
            for act in ['northeast','northwest','southeast','southwest']:
                self.templates.remove(act)
            self.templates.extend(['ne','nw','se','sw'])

    def _preprocess_templates(self, templates, max_word_length):
        '''
        Converts templates with multiple verbs and takes the first verb.

        '''
        out = []
        vb_usage_fn = lambda verb: verb_usage_count(verb, max_word_length)
        p = re.compile('\S+(/\S+)+')
        for template in templates:
            if not template:
                continue
            while True:
                match = p.search(template)
                if not match:
                    break
                verb = max(match.group().split('/'), key=vb_usage_fn)
                template = template[:match.start()] + verb + template[match.end():]
            ts = template.split()
            if ts[0] in defines.ILLEGAL_ACTIONS:
                continue
            if ts[0] in defines.NO_EFFECT_ACTIONS and len(ts) == 1:
                continue
            out.append(template)
        return out


    def generate_actions(self, objs):
        '''
        Given a list of objects present at the current location, returns
        a list of possible actions. This list represents all combinations
        of templates filled with the provided objects.

        :param objs: Candidate interactive objects present at the current location.
        :type objs: List of strings
        :returns: List of action-strings.

        :Example:

        >>> import jericho
        >>> from jericho.template_action_generator import TemplateActionGenerator
        >>> bindings = jericho.load_bindings(rom_path)
        >>> act_gen = TemplateActionGenerator(bindings)
        >>> interactive_objs = ['phone', 'keys', 'wallet']
        >>> act_gen.generate_actions(interactive_objs)
        ['wake', 'wake up', 'wash', ..., 'examine wallet', 'remove phone', 'taste keys']

        '''
        actions = []
        for template in self.templates:
            holes = template.count('OBJ')
            if holes <= 0:
                actions.append(template)
            elif holes == 1:
                actions.extend([template.replace('OBJ', obj) for obj in objs])
            elif holes == 2:
                for o1 in objs:
                    for o2 in objs:
                        if o1 != o2:
                            actions.append(template.replace('OBJ', o1, 1).replace('OBJ', o2, 1))
        return actions


    def generate_template_actions(self, objs, obj_ids):
        '''
        Given a list of objects and their corresponding vocab_ids, returns
        a list of possible TemplateActions. This list represents all combinations
        of templates filled with the provided objects.

        :param objs: Candidate interactive objects present at the current location.
        :type objs: List of strings
        :param obj_ids: List of ids corresponding to the tokens of each object.
        :type obj_ids: List of int
        :returns: List of :class:`jericho.defines.TemplateAction`.

        :Example:

        >>> import jericho
        >>> from jericho.template_action_generator import TemplateActionGenerator
        >>> bindings = jericho.load_bindings(rom_path)
        >>> act_gen = TemplateActionGenerator(bindings)
        >>> interactive_objs = ['phone', 'keys', 'wallet']
        >>> interactive_obj_ids = [718, 325, 64]
        >>> act_gen.generate_template_actions(interactive_objs, interactive_obj_ids)
        [
          TemplateAction(action='wake', template_id=0, obj_ids=[]),
          TemplateAction(action='wake up', template_id=1, obj_ids=[]),
          ...
          TemplateAction(action='turn phone on', template_id=55, obj_ids=[718]),
          TemplateAction(action='put wallet on keys', template_id=65, obj_ids=[64, 325])
         ]

        '''
        assert len(objs) == len(obj_ids)
        actions = []
        for template_idx, template in enumerate(self.templates):
            holes = template.count('OBJ')
            if holes <= 0:
                actions.append(defines.TemplateAction(template, template_idx, []))
            elif holes == 1:
                for noun, noun_id in zip(objs, obj_ids):
                    actions.append(
                        defines.TemplateAction(template.replace('OBJ', noun),
                                               template_idx, [noun_id]))
            elif holes == 2:
                for o1, o1_id in zip(objs, obj_ids):
                    for o2, o2_id in zip(objs, obj_ids):
                        if o1 != o2:
                            actions.append(
                                defines.TemplateAction(
                                    template.replace('OBJ', o1, 1).replace('OBJ', o2, 1),
                                    template_idx, [o1_id, o2_id]))
        return actions
