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

// Dragon Adventure: http://ifdb.tads.org/viewgame?id=sjiyffz8n5patu8l

const zword dragon_special_ram_addrs[3] = {
  16090, // Set to 1 when you buy the box
  16101, // Set to 1 when you play the flute
  16102 // Set to 1 when you blow the horn
};

zword* dragon_ram_addrs(int *n) {
    *n = 3;
    return dragon_special_ram_addrs;
}

char** dragon_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* dragon_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int dragon_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int dragon_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game or QUIT";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int dragon_get_self_object_num() {
  return 20;
}

int dragon_get_moves() {
  return (((short) zmp[13452]) << 8) | zmp[13453]; // 13465
}

short dragon_get_score() {
  return (char) zmp[13451]; // 13475, 13477
}

int dragon_max_score() {
  return 25;
}

int dragon_get_num_world_objs() {
  return 268;
}

int dragon_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int dragon_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 52 && attr_idx == 17)
    return 1;
  if (attr_idx == 25)
    return 1;
  return 0;
}

int dragon_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void dragon_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 7) & ~(1 << 6);
    // Clear attr 24 & 25
    for (i=1; i<=dragon_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
