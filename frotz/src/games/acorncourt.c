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

// The Acorn Court: http://ifdb.tads.org/viewgame?id=tqvambr6vowym20v

const zword acorn_special_ram_addrs[4] = {
  3641, // Counts number of holes in bucket
  3687, // Boolean if machine aimed at tree
  3694, // Boolean if rope tied to bucket
  3699  // Boolean if bucket is raised or lowered (e.g. turn crank)
};

zword* acorn_ram_addrs(int *n) {
  *n = 4;
  return acorn_special_ram_addrs;
}

char** acorn_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* acorn_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '[');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int acorn_victory() {
    char *victory_text = "*** You have won ***";
    if (strstr(world, victory_text)) {
        return 1;
    }
    return 0;
}

int acorn_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game or QUIT?";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int acorn_get_self_object_num() {
  return 20;
}

int acorn_get_moves() {
  return (((short) zmp[3711]) << 8) | zmp[3712];
}

short acorn_get_score() {
  return zmp[3710]; // Also 3734 and 3736
}

int acorn_max_score() {
  return 30;
}

int acorn_get_num_world_objs() {
  return 63;
}

int acorn_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int acorn_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int acorn_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void acorn_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 6);
    // Clear attr 25
    for (i=1; i<=acorn_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
