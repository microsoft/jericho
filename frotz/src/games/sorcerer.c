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

// Sorcerer: http://ifdb.tads.org/viewgame?id=lidg5nx9ig0bwk55

zword* sorcerer_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** sorcerer_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* sorcerer_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int sorcerer_victory() {
  char *death_text = "Once again, this young Enchanter has done a matchless service to the Guild";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int sorcerer_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int sorcerer_get_self_object_num() {
  return 223;
}

int sorcerer_get_moves() {
  return (((short) zmp[9700]) << 8) | zmp[9701];
}

short sorcerer_get_score() {
  return (((short) zmp[9698]) << 8) | zmp[9699];
}

int sorcerer_max_score() {
  return 400;
}

int sorcerer_get_num_world_objs() {
  return 255;
}

int sorcerer_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int sorcerer_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int sorcerer_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void sorcerer_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 5);
    // Clear attr 18
    for (i=1; i<=sorcerer_get_num_world_objs(); ++i) {
        objs[i].attr[2] &= mask;
    }
}
