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

// Zork II: http://ifdb.tads.org/viewgame?id=yzzm4puxyjakk8c4

zword* zork2_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** zork2_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* zork2_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int zork2_victory() {
  char *death_text = "The ultimate adventure concludes in \"Zork III: The Dungeon Master\".";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int zork2_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int zork2_get_self_object_num() {
  return 4;
}

int zork2_get_moves() {
  return (((short) zmp[8937]) << 8) | zmp[8938];
}

short zork2_get_score() {
  return (((short) zmp[8935]) << 8) | zmp[8936]; // 9110
}

int zork2_max_score() {
  return 400;
}

int zork2_get_num_world_objs() {
  return 250;
}

int zork2_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int zork2_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int zork2_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void zork2_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 5);
    // Clear attr 2
    for (i=1; i<=zork2_get_num_world_objs(); ++i) {
        objs[i].attr[0] &= mask;
    }
}
