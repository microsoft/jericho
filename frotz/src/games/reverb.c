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

// Reverberations: http://ifdb.tads.org/viewgame?id=dop7nbjl90r5zmf9

char** reverb_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* reverb_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int reverb_victory() {
  char *death_text = "****  You have won  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int reverb_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int reverb_get_self_object_num() {
  return 20;
}

int reverb_get_moves() {
  return (((short) zmp[5840]) << 8) | zmp[5841]; //5853
}

int reverb_get_score() {
  return zmp[5839]; //5863, 5865
}

int reverb_max_score() {
  return 50;
}

int reverb_get_num_world_objs() {
  return 120;
}

int reverb_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int reverb_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 31)
    return 1;
  return 0;
}

int reverb_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 31)
    return 1;
  return 0;
}
