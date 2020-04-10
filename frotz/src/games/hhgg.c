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

// Hitchhiker's Guide to the Galaxy: http://ifdb.tads.org/viewgame?id=ouv80gvsl32xlion

zword* hhgg_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** hhgg_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* hhgg_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int hhgg_victory() {
  char *death_text = "You step onto the landing ramp";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hhgg_game_over() {
  char *death_text = "(Type RESTART, RESTORE, or QUIT)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hhgg_get_self_object_num() {
  return 31;
}

int hhgg_get_moves() {
  return (((short) zmp[7912]) << 8) | zmp[7913];
}

short hhgg_get_score() {
  return (((short) zmp[7910]) << 8) | zmp[7911];
}

int hhgg_max_score() {
  return 400;
}

int hhgg_get_num_world_objs() {
  return 220;
}

int hhgg_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int hhgg_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 31 && attr_idx == 17)
    return 1;
  return 0;
}

int hhgg_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (obj_num == 31 && attr_idx == 17)
    return 1;
  return 0;
}

void hhgg_clean_world_objs(zobject* objs) {
}
