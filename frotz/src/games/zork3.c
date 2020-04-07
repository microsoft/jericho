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

// Zork III: http://ifdb.tads.org/viewgame?id=vrsot1zgy1wfcdru

zword* zork3_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** zork3_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* zork3_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int zork3_victory() {
  char *death_text = "you have at last completed your quest in ZORK";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int zork3_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int zork3_get_self_object_num() {
  return 202;
}

int zork3_get_moves() {
  return (((short) zmp[7956]) << 8) | zmp[7957];
}

short zork3_get_score() {
  return zmp[7955];
}

int zork3_max_score() {
  return 7;
}

int zork3_get_num_world_objs() {
  return 219;
}

int zork3_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int zork3_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int zork3_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void zork3_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 4);
    // Clear attr 27
    for (i=1; i<=zork3_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
