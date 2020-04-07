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

// Hunter, in Darkness: http://ifdb.tads.org/viewgame?id=mh1a6hizgwjdbeg7

const char *huntdark_intro[] = { "\n", "\n" };

zword* huntdark_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** huntdark_intro_actions(int *n) {
  *n = 2;
  return huntdark_intro;
}

char* huntdark_clean_observation(char* obs) {
  char* pch;
  pch = strstr(obs, ">  ");
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int huntdark_victory() {
  char *death_text = "*** It's over ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int huntdark_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int huntdark_get_self_object_num() {
  return 17;
}

int huntdark_get_moves() {
  return (((short) zmp[8896]) << 8) | zmp[8897];
}

short huntdark_get_score() {
  if (huntdark_victory()) {
    return 1;
  }
  return 0;
}

int huntdark_max_score() {
  return 1;
}

int huntdark_get_num_world_objs() {
  return 151;
}

int huntdark_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int huntdark_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  return 0;
}

int huntdark_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  return 0;
}

void huntdark_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 6);
    // Clear attr 25
    for (i=1; i<=huntdark_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
