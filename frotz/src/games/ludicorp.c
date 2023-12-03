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

// The Ludicorp Mystery: http://ifdb.tads.org/viewgame?id=r6g7pflngn3uxbam

const zword ludicorp_special_ram_addrs[2] = {
  24139,  // Tracks button presses
  24158,  // Tracks punch card
};


zword* ludicorp_ram_addrs(int *n) {
    *n = 2;
    return ludicorp_special_ram_addrs;
}

char** ludicorp_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* ludicorp_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int ludicorp_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int ludicorp_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ludicorp_get_self_object_num() {
  return 20;
}

int ludicorp_get_moves() {
  return (((short) zmp[24205]) << 8) | zmp[24206]; //24194
}

short ludicorp_get_score() {
  return zmp[24216]; //24192, 24218
}

int ludicorp_max_score() {
  return 150;
}

int ludicorp_get_num_world_objs() {
  return 392;
}

int ludicorp_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int ludicorp_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int ludicorp_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void ludicorp_clean_world_objs(zobject* objs) {
    for (int i=1; i<=ludicorp_get_num_world_objs(); ++i) {
        clear_attr(&objs[i], 24);
        clear_attr(&objs[i], 25);
    }
}
