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

// Monsters of Murdac: http://ifdb.tads.org/viewgame?id=q36lh5np0q9nak28

zword* murdac_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** murdac_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* murdac_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int murdac_victory() {
  char *victory_text = "are taken off in triumph to the land of Heroes of Murdac";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int murdac_game_over() {
  char *death_text = "Another game, your Extravagance?";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int murdac_get_self_object_num() {
  return 7;
}

int murdac_get_moves() {
  return (((short) zmp[6372]) << 8) | zmp[6373]; //6375,6383
}

short murdac_get_score() {
  return zmp[6357];
}

int murdac_max_score() {
  return 250;
}

int murdac_get_num_world_objs() {
  return 126;
}

int murdac_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int murdac_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 1)
    return 1;
  return 0;
}

int murdac_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 1)
    return 1;
  return 0;
}

void murdac_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 6);
    // Clear attr 1
    for (i=1; i<=murdac_get_num_world_objs(); ++i) {
        objs[i].attr[0] &= mask;
    }
}
