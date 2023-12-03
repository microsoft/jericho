
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

// The Lurking Horror: http://ifdb.tads.org/viewgame?id=jhbd0kja1t57uop

const zword lurking_special_ram_addrs[11] = {
  // 4889, // Drinking coke
  // 756, // knock on door
  1047, // Lower ladder (alt. 1163, 1333)
  1067, // Move lab bench.
  11235, // press up/down button
  11251, // Microwave timer
  1145, // Cleaning up junk
  813, // Throw axe at cord
  859, // Read page, click on more, again and again.
  883, // Cut line with axe
  883, // Cutting line
  935, // Position of valve
  961, // Microwave setting
  // 1132, 1133, // Microwave timer
};

const char *lurking_intro[] = { "sit on chair\n",
                                "turn pc on\n",
                                "login 872325412\n",
                                "password uhlersoth\n" };

zword* lurking_ram_addrs(int *n) {
    *n = 11;
    return lurking_special_ram_addrs;
}

char** lurking_intro_actions(int *n) {
  *n = 4;
  return lurking_intro;
}

char* lurking_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int lurking_victory() {
  char *death_text = "The hacker, mud-covered and weak, staggers to his feet. \"Can I have my key back?\" he asks.";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int lurking_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int lurking_get_self_object_num() {
  return 56;
}

int lurking_get_moves() {
  return (((short) zmp[696]) << 8) | zmp[697];
}

short lurking_get_score() {
  return zmp[695];
}

int lurking_max_score() {
  return 100;
}

int lurking_get_num_world_objs() {
  return 252;
}

int lurking_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int lurking_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int lurking_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void lurking_clean_world_objs(zobject* objs) {
  for (int i=1; i<=lurking_get_num_world_objs(); ++i) {
    clear_attr(&objs[i], 6);
    clear_attr(&objs[i], 10);
  }

  clear_attr(&objs[183], 11);  // sign-up sheet

  clear_prop(&objs[90], 3);  // Chinese food.
  clear_prop(&objs[206], 16);  // Infinite Corridor.

  // Completely ignore the 'pseudo' object.
  strcpy(&objs[247].name, "pseudo");  // Its name reflects what the player's focus.

  objs[100].parent = 0;  // urchin
  objs[235].parent = 0;  // waxer
  objs[20].parent = 0;  // man

  if (objs[56].parent != objs[122].parent) {  // If player is not in the same room as the doors.
    clear_attr(&objs[122], 13);  // doors
    clear_attr(&objs[225], 13);  // doors
  }

  objs[143].parent = 0;  // tangle machinery
  objs[153].parent = 0;  // tangle machinery

  // // Track whether player has knocked on the Alchemy door.
  int N = 23;  // Use last property slot.
  objs[108].prop_ids[N-1] = 63;
  objs[108].prop_lengths[N-1] = 1;
  objs[108].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH] = (zmp[9306] == 140 && zmp[9307] == 121);
}
