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

#include <stdlib.h>
#include <string.h>
#include "frotz.h"
#include "games.h"
#include "frotz_interface.h"

// Afflicted: http://ifdb.tads.org/viewgame?id=epl4q2933rczoo9x

int score = 0;

const zword afflicted_special_ram_addrs[3] = {
  25038, // Nikolai's sanitation rating. Alternative: 24989, 24997, 25039
  1880, // Angela wakes up
  // 25461, // Noting things.
  24996 // Sofia is dead.
};

zword* afflicted_ram_addrs(int *n) {
    *n = 3;
    return afflicted_special_ram_addrs;
}

char** afflicted_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

void parse_score(char* obs) {
  char* pch = obs;
  char* old = pch;
  while (TRUE) {
    pch = strchr(pch, ':');
    if (pch == NULL) {
      break;
    }
    pch++;
    old = pch;
  }
  score = -strtol(old, &old, 10);
}

char* afflicted_clean_observation(char* obs) {
  parse_score(obs);
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int afflicted_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int afflicted_game_over() {
  char *death_text = "*** You've been convicted. ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int afflicted_get_self_object_num() {
  return 57;
}

int afflicted_get_moves() {
  return (((short) zmp[24991]) << 8) | zmp[24992]; // 25032, 25034
}

short afflicted_get_score() {
  return score;
}

int afflicted_max_score() {
  return 75;
}

int afflicted_get_num_world_objs() {
  return 237;
}

int afflicted_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int afflicted_ignore_attr_diff(zword obj_num, zword attr_idx) {
  // if (attr_idx == 30 || attr_idx == 11 || attr_idx == 34 || attr_idx == 21)
  if (attr_idx == 30 || attr_idx == 29)
    return 1;
  return 0;
}

int afflicted_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 30 || attr_idx == 29)
    return 1;
  return 0;
}

void afflicted_clean_world_objs(zobject* objs) {
  // Zero out attribute 30 for all objects.
  // attr[0]  attr[1]  attr[2]  attr[3]
  // 11111111 11111111 11111111 11111001
  char mask3 = 0b11111001;  // Attr 29 and 30.
  for (int i=1; i<=afflicted_get_num_world_objs(); ++i) {
      objs[i].attr[3] &= mask3;
  }

  // Zero out Prop28 some objects with no name.
  int N;
  N = 5;  // Prop28.
  memset(&objs[204].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[204].prop_lengths[N-1] * sizeof(zbyte));
  memset(&objs[205].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[205].prop_lengths[N-1] * sizeof(zbyte));
  memset(&objs[206].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[206].prop_lengths[N-1] * sizeof(zbyte));
  memset(&objs[207].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[207].prop_lengths[N-1] * sizeof(zbyte));

}
