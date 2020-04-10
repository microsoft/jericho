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

// The Temple: http://ifdb.tads.org/viewgame?id=kq9qgjkf2k6xn1c0

zword* temple_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** temple_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* temple_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int temple_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int temple_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int temple_get_self_object_num() {
  return 89;
}

int temple_get_moves() {
  return (((short) zmp[8310]) << 8) | zmp[8311]; //8321
}

short temple_get_score() {
  return zmp[8309]; //8319
}

int temple_max_score() {
  return 35;
}

int temple_get_num_world_objs() {
  return 158;
}

int temple_ignore_moved_obj(zword obj_num, zword dest_num) {
  if (obj_num == 92 || obj_num == 94)
    return 1;
  return 0;
}

int temple_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  if (obj_num == 92 && attr_idx == 9)
    return 1;
  return 0;
}

int temple_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  if (obj_num == 92 && attr_idx == 9)
    return 1;
  return 0;
}

void temple_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 6);
    // Clear attr 25
    for (i=1; i<=temple_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
