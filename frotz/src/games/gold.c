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

// Goldilocks is a FOX!: http://ifdb.tads.org/viewgame?id=59ztsy9p01avd6wp

const zword gold_special_ram_addrs[9] = {
    1025, // Eating porridge
    20672, // Move wardrobe (Also 23313)
    18314, // Oil secateurs
    8251, // TV Channel
    17125, // Unplug TV
    20747, // Toaster lever (Also 3307)
    23342, // Kiss frog (Also 2697, 2709)
    20722, // Give pumpkin to fairy godmother (Also 23331)
    20762, // Say Alakazam (Also 20403, 21927, 19416)
};

zword* gold_ram_addrs(int *n) {
    *n = 9;
    return gold_special_ram_addrs;
}

char** gold_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* gold_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int gold_victory() {
  char *death_text = "The important thing is, our plan worked!";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int gold_game_over() {
  char *death_text = "Would I like to RESTART";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int gold_get_self_object_num() {
  return 85;
}

int gold_get_moves() {
  return (((short) zmp[20789]) << 8) | zmp[20790];
}

short gold_get_score() {
  return zmp[20768]; // 20800, 20802
}

int gold_max_score() {
  return 100;
}

int gold_get_num_world_objs() {
  return 255;
}

int gold_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int gold_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25 || attr_idx == 31)
    return 1;
  return 0;
}

int gold_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25 || attr_idx == 31)
    return 1;
  return 0;
}

void gold_clean_world_objs(zobject* objs) {
}
