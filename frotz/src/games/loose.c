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

// Mother Loose: http://ifdb.tads.org/viewgame?id=4wd3lyaxi4thp8qi

const char *loose_intro[] = { "\n" };

zword* loose_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** loose_intro_actions(int *n) {
  *n = 1;
  return loose_intro;
}

char* loose_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int loose_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int loose_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int loose_get_self_object_num() {
  return 34;
}

int loose_get_moves() {
  return (((short) zmp[10392]) << 8) | zmp[10393]; // 10405
}

short loose_get_score() {
  return zmp[10391]; // 10415, 10417
}

int loose_max_score() {
  return 50;
}

int loose_get_num_world_objs() {
  return 178;
}

int loose_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int loose_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int loose_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void loose_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 7) & ~(1 << 6);
    // Clear attr 24 & 25
    for (i=1; i<=loose_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
