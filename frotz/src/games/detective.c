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

// Detective: http://ifdb.tads.org/viewgame?id=1po9rgq2xssupefw

zword* detective_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** detective_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* detective_clean_observation(char* obs) {
  char* pch;
  pch = strstr(obs, ">  ");
  if (pch != NULL) {
    *(pch-1) = '\0';
  }
  return obs;
}

int detective_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int detective_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int detective_get_self_object_num() {
  return 90;
}

int detective_get_moves() {
  return (((short) zmp[6777]) << 8) | zmp[6778]; // 6792
}

short detective_get_score() {
  return (((short) zmp[6801]) << 8) | zmp[6802]; // Also 6776, 6804
}

int detective_max_score() {
  return 360;
}

int detective_get_num_world_objs() {
  return 101;
}

int detective_ignore_moved_obj(zword obj_num, zword dest_num) {
  // Detective has an issue where if you select invalid movement
  // actions any location, it re-moves the player object to that
  // location.
  return 0;
}

int detective_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  return 0;
}

int detective_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 26)
    return 1;
  return 0;
}

void detective_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 6) & ~(1 << 5);
    // Clear attr 25 & 26
    for (i=1; i<=detective_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
