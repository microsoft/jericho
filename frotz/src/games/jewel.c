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

// The Jewel of Knowledge: http://ifdb.tads.org/viewgame?id=hu60gp1bgkhlo5yx

const char *jewel_intro[] = { "bypass\n", "yes\n" };

const zword jewel_special_ram_addrs[1] = {
  1796, // Chop ice
};

zword* jewel_ram_addrs(int *n) {
    *n = 1;
    return jewel_special_ram_addrs;
}

char** jewel_intro_actions(int *n) {
  *n = 2;
  return jewel_intro;
}

char* jewel_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int jewel_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int jewel_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int jewel_get_self_object_num() {
  return 211;
}

int jewel_get_moves() {
  return (((short) zmp[9971]) << 8) | zmp[9972]; // 9984
}

short jewel_get_score() {
  return zmp[9970]; //9996,9994
}

int jewel_max_score() {
  return 90;
}

int jewel_get_num_world_objs() {
  return 211;
}

int jewel_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int jewel_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int jewel_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void jewel_clean_world_objs(zobject* objs) {
  for (int i=1; i<=jewel_get_num_world_objs(); ++i) {
    clear_attr(&objs[i], 25);
  }

  clear_prop(&objs[58], 41);  // geyser's counter
  clear_prop(&objs[60], 41);  // Shaft Base's counter
  clear_prop(&objs[61], 41);  // Middle Shaft's counter
  clear_prop(&objs[62], 41);  // Top of the Shaft's counter
  clear_prop(&objs[66], 41);  // On the Ledge's counter
  clear_prop(&objs[143], 41);  // Black Dargon's Lair's counter
  clear_prop(&objs[148], 41);  // At the Top of the Ramp's counter
  clear_prop(&objs[153], 41);  // Black Dragon's Antechamber's counter
  clear_prop(&objs[159], 41);  // Well-Lit Passage's counter
  clear_prop(&objs[162], 41);  // Steep Cliff Face's counter
  clear_prop(&objs[164], 41);  // Red Dragon Gate's counter
  clear_prop(&objs[167], 41);  // Red Dragon Lair's counter
  clear_prop(&objs[170], 41);  // On The Divide's counter
  clear_prop(&objs[174], 41);  // Red Dragon's Plateau's counter
  clear_prop(&objs[180], 41);  // In the River's counter
  clear_prop(&objs[182], 41);  // Underground River's counter
}
