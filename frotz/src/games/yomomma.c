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

// Raising the Flag on Mount Yomomma - http://ifdb.tads.org/viewgame?id=1iqmpkn009h9gbug

const zword yomomma_special_ram_addrs[8] = {
  21060, // Climb on stage
  16005, // Counts stage victories
  36238, // Discovered Ralph's secrets
  21072, // Insult Vincent.
  15643, // Set thermostat to warm
  16638, // Take Gus' sweater.
  36226, // Talk to britney to learn Gus' secret. (alt. 26050, 36202)
  14110, // Turn music up.
  // 36248, // Set thermostat to warm + give cola to guard
};

zword* yomomma_ram_addrs(int *n) {
    *n = 8;
    return yomomma_special_ram_addrs;
}

char** yomomma_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* yomomma_clean_observation(char* obs) {
  char* pch;
  pch = strstr(obs, ">  ");
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int yomomma_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int yomomma_game_over() {
  char *death_text = "***GAME OVER***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int yomomma_get_self_object_num() {
  return 59;
}

int yomomma_get_moves() {
  return (((short) zmp[15532]) << 8) | zmp[15533];
}

short yomomma_get_score() {
  return zmp[15531];
}

int yomomma_max_score() {
  return 35;
}

int yomomma_get_num_world_objs() {
  return 139;
}

int yomomma_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int yomomma_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 30)
    return 1;
  return 0;
}

int yomomma_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 30)
    return 1;
  return 0;
}

void yomomma_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 2);
    // Clear attr 21
    for (i=1; i<=yomomma_get_num_world_objs(); ++i) {
        objs[i].attr[2] &= mask;
    }
}
