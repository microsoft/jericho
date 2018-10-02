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

// Zork: The Undiscovered Underground: http://ifdb.tads.org/viewgame?id=40hswtkhap88gzvn

char** ztuu_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* ztuu_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int ztuu_victory() {
  char *death_text = "****  You have won  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ztuu_game_over() {
  char *death_text = "Would you like to RESTART";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ztuu_get_self_object_num() {
  return 20;
}

int ztuu_get_moves() {
  return zmp[8857]; //8867
}

int ztuu_get_score() {
  return zmp[8855]; //8881, 8865
}

int ztuu_max_score() {
  return 100;
}

int ztuu_get_num_world_objs() {
  return 180;
}

int ztuu_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int ztuu_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int ztuu_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}
