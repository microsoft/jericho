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

// Return to Karn: http://ifdb.tads.org/viewgame?id=bx8118ggp6j7nslo

const zword karn_special_ram_addrs[5] = {
  14066, // Tardis flying/grounded
  13050, // Color sequence
  1213, // k9 following player
  2194, // Pull lever and Push button
  3101, // Pull pipe
};

zword* karn_ram_addrs(int *n) {
    *n = 5;
    return karn_special_ram_addrs;
}

char** karn_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* karn_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int karn_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int karn_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int karn_get_self_object_num() {
  return 20;
}

int karn_get_moves() {
  return (((short) zmp[13817]) << 8) | zmp[13818]; // 13828
}

short karn_get_score() {
  return zmp[13816]; // 13826, 13842
}

int karn_max_score() {
  return 170;
}

int karn_get_num_world_objs() {
  return 274;
}

int karn_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int karn_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int karn_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void karn_clean_world_objs(zobject* objs) {
  for (int i=1; i<=karn_get_num_world_objs(); ++i) {
    clear_attr(&objs[i], 25);
    clear_attr(&objs[i], 8);
  }

  clear_prop(&objs[253], 25);  // firework's counter
  clear_prop(&objs[254], 25);  // match's counter
}
