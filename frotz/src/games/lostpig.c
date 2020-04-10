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

// Lost Pig: http://ifdb.tads.org/viewgame?id=mohwfk47yjzii14w

zword* lostpig_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** lostpig_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* lostpig_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int lostpig_victory() {
  char *victory_text = "***  Grunk bring pig back to farm  ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int lostpig_game_over() {
  char *death_text = "Time for Grunk to RESTART or RESTORE a saved story or UNDO";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int lostpig_get_self_object_num() {
  return 87;
}

int lostpig_get_moves() {
  return (((short) zmp[39582]) << 8) | zmp[39583]; // 39607
}

short lostpig_get_score() {
  return zmp[39581]; //39617, 39619
}

int lostpig_max_score() {
  return 7;
}

int lostpig_get_num_world_objs() {
  return 535;
}

int lostpig_ignore_moved_obj(zword obj_num, zword dest_num) {
  if (obj_num != 87 && dest_num != 87)
    return 1;
  return 0;
}

int lostpig_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 14 || attr_idx == 15)
    return 1;
  return 0;
}

int lostpig_ignore_attr_clr(zword obj_num, zword attr_idx) {
  /* if (attr_idx == 14 || attr_idx == 15) */
  return 1;
  /* return 0; */
}

void lostpig_clean_world_objs(zobject* objs) {
}
