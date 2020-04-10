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

// Ballyhoo: http://ifdb.tads.org/viewgame?id=b0i6bx7g4rkrekgg

zword* ballyhoo_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** ballyhoo_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* ballyhoo_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int ballyhoo_victory() {
  char *death_text = "having saved The Traveling Circus That Time Forgot, Inc.";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ballyhoo_game_over() {
  char *death_text = "(Type RESTART, RESTORE, or QUIT)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ballyhoo_get_self_object_num() {
  return 211;
}

int ballyhoo_get_moves() {
  return (((short) zmp[8496]) << 8) | zmp[8497];
}

short ballyhoo_get_score() {
  return zmp[8495];
}

int ballyhoo_max_score() {
  return 200;
}

int ballyhoo_get_num_world_objs() {
  return 235;
}

int ballyhoo_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int ballyhoo_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 211 && attr_idx == 13)
    return 1;
  if (attr_idx == 30)
    return 1;
  return 0;
}

int ballyhoo_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (obj_num == 211 && attr_idx == 13)
    return 1;
  if (attr_idx == 20)
    return 1;
  return 0;
}

void ballyhoo_clean_world_objs(zobject* objs) {
}
