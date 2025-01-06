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

// Enchanter: http://ifdb.tads.org/viewgame?id=vu4xhul3abknifcr

const zword enchanter_special_ram_addrs[3] = {
  9082, // Move block.
  8906, // Drawing lines on the map.
  8984, // Erasing lines on the map.
};

zword* enchanter_ram_addrs(int *n) {
    *n = 3;
    return enchanter_special_ram_addrs;
}

char** enchanter_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* enchanter_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int enchanter_victory() {
  char *death_text = "Here ends the first chapter of the Enchanter saga";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int enchanter_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int enchanter_get_self_object_num() {
  return 55;
}

int enchanter_get_moves() {
  return (((short) zmp[8767]) << 8) | zmp[8768]; //9080
}

short enchanter_get_score() {
  return (((short) zmp[8765]) << 8 ) | zmp[8766];
}

int enchanter_max_score() {
  return 400;
}

int enchanter_get_num_world_objs() {
  return 255;
}

int enchanter_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int enchanter_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int enchanter_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void enchanter_clean_world_objs(zobject* objs) {
  // int i;
  // char mask;
  // mask = ~1;
  // // Clear attr 15
  // for (i=1; i<=enchanter_get_num_world_objs(); ++i) {
  //     objs[i].attr[1] &= mask;
  // }
  clear_attr(&objs[55], 10);  // cretin a.k.a. the player
  clear_attr(&objs[122], 17);  // Temple
  clear_attr(&objs[87], 17);  // Cell
  clear_attr(&objs[142], 17);  // Courtyard
  clear_attr(&objs[66], 17);  // Courtyard
  clear_attr(&objs[190], 17);  // Courtyard
  clear_attr(&objs[116], 17);  // Courtyard
  clear_attr(&objs[167], 16);  // Frobozz portrait
  clear_attr(&objs[179], 16);  // Flathead portrait
  clear_attr(&objs[242], 16);  // no-name object
  clear_attr(&objs[27], 17);  // Kitchen
  clear_attr(&objs[64], 17);  // North Gate
  clear_attr(&objs[64], 15);  // North Gate
  clear_attr(&objs[43], 17);  // East Hall
  clear_attr(&objs[43], 15);  // East Hall
  clear_attr(&objs[47], 15);  // Winding Stair

  // Completely ignore the 'pseudo' object.
  strcpy(&objs[252].name, "pseudo");  // Its name reflects what the player's focus.
  clear_prop(&objs[252], 9);

}