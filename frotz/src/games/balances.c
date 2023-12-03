/*
Copyright (C) 2018 Microsoft Corporation

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
*/


#include <string.h>
#include "frotz.h"
#include "games.h"
#include "frotz_interface.h"

// Balances: http://ifdb.tads.org/viewgame?id=x6ne0bbd2oqm6h3a

const zword balances_special_ram_addrs[0] = {
    // 4162, // Write cave on cube
    // 1217, // urbzig snake (Also 1219, 3776)
    // 3760, // write chasm on cube
    // 5086, // Give silver to barker
    // 3327, // Keeps track of number of yomins memorized
    // 5217, // write prize on featureless
    // 4640, // write mace on featureless
    // 4589, // Process to acquire the mace cube
    // 1581, // urbzig toy and mace (Also 1583)
};

zword* balances_ram_addrs(int *n) {
    *n = 0;
    return balances_special_ram_addrs;
}

char** balances_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* balances_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int balances_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int balances_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int balances_get_self_object_num() {
  return 20;
}

int balances_get_moves() {
  return (((short) zmp[6843]) << 8) | zmp[6844];
}

short balances_get_score() {
  return zmp[6842]; // Also 6866, 6868
}

int balances_max_score() {
  return 51;
}

int balances_get_num_world_objs() {
  return 124;
}

int balances_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int balances_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int balances_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void balances_clean_world_objs(zobject* objs) {
  // Zero out attribute 8, 25 and 31 for all objects.
  // attr[0]  attr[1]  attr[2]  attr[3]
  // 11111111 01111111 11111111 11111110
  char mask1 = 0b01111111;  // Attr 8
  char mask3 = 0b10111110;  // Attr 25, 31
  for (int i=1; i<=balances_get_num_world_objs(); ++i) {
      objs[i].attr[1] &= mask1;
      objs[i].attr[3] &= mask3;
  }

  int N;
  // Zero out the lobal_spell's counter.
  N = 4;  // Prop40.
  memset(&objs[65].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[65].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the buck-toothed cyclops's counter.
  N = 3;  // Prop40.
  memset(&objs[86].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[86].prop_lengths[N-1] * sizeof(zbyte));
}
