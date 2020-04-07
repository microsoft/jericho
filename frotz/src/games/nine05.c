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

// 9:05 - http://ifdb.tads.org/viewgame?id=qzftg3j8nh5f34i2

zword* nine05_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** nine05_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* nine05_clean_observation(char* obs) {
  char* pch;
  pch = strstr(obs, ">  ");
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int nine05_victory() {
  char *death_text = "*** You have left Las Mesas ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int nine05_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int nine05_get_self_object_num() {
  return 28;
}

int nine05_get_moves() {
  return ((((short) zmp[4295]) << 8) | zmp[4296]) - 545;
}

short nine05_get_score() {
  if (nine05_victory()) {
    return 1;
  }
  return 0;
}

int nine05_max_score() {
  return 1;
}

int nine05_get_num_world_objs() {
  return 84;
}

int nine05_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int nine05_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int nine05_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void nine05_clean_world_objs(zobject* objs) {
}
