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

// Inhumane: http://ifdb.tads.org/viewgame?id=wvs2vmbigm9unlpd

zword* inhumane_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** inhumane_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* inhumane_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int inhumane_victory() {
  char *victory_text = "--end of session--";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int inhumane_game_over() {
  // You have to die 9 times to solve this one
  return 0;
}

int inhumane_get_self_object_num() {
  return 15;
}

int inhumane_get_moves() {
  return (((short) zmp[4788]) << 8) | zmp[4789]; // 4799
  /* return zmp[4789]; //4799 */
}

short inhumane_get_score() {
  return zmp[4787]; // 4797
}

int inhumane_max_score() {
  return 90;
}

int inhumane_get_num_world_objs() {
  return 108;
}

int inhumane_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int inhumane_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 27)
    return 1;
  return 0;
}

int inhumane_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 27)
    return 1;
  return 0;
}

void inhumane_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 5);
    // Clear attr 26
    for (i=1; i<=inhumane_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
