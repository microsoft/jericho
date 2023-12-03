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

// Omniquest: http://ifdb.tads.org/viewgame?id=mygqz9tzxqvryead

const zword omniquest_special_ram_addrs[0] = {
  // 2123 // Keep track of whether you've given sushi to samurai; Also 2135.
};

zword* omniquest_ram_addrs(int *n) {
    *n = 0;
    return omniquest_special_ram_addrs;
}

char** omniquest_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* omniquest_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int omniquest_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int omniquest_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int omniquest_get_self_object_num() {
  return 20;
}

int omniquest_get_moves() {
  return (((short) zmp[5980]) << 8) | zmp[5981]; //5995
}

short omniquest_get_score() {
  return zmp[5979]; //6005, 6007
}

int omniquest_max_score() {
  return 50;
}

int omniquest_get_num_world_objs() {
  return 138;
}

int omniquest_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int omniquest_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int omniquest_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void omniquest_clean_world_objs(zobject* objs) {
  for (int i=1; i<=omniquest_get_num_world_objs(); ++i) {
      clear_attr(&objs[i], 24);
      clear_attr(&objs[i], 25);
  }
  clear_prop(&objs[138], 40);  // (long_time)
}
