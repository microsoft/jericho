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

// Mother Loose: http://ifdb.tads.org/viewgame?id=4wd3lyaxi4thp8qi

const char *loose_intro[] = { "\n" };

const zword loose_special_ram_addrs[1] = {
  13292, // going north to go home with your mother.
};

zword* loose_ram_addrs(int *n) {
    *n = 1;
    return loose_special_ram_addrs;
}

char** loose_intro_actions(int *n) {
  *n = 1;

  // Patch bug in source file.
  // Routine 14370, 0 locals
  // 14371:  JE              G00,#88 [FALSE] 1437e
  // 14375:  CALL_VN         18cbc (Geb,#23)
  //
  // Geb refers to object 150 (hillside) where its property #23 is pointing
  // to routine 14370 which ultimately creates an infinite recursive loop.
  // Swapping Geb for G00, which refers to object 136 (hilltop), avoids the
  // infinite loop and outputs the expected description of the hilltop.
  zmp[0x14379] = 0x10;  // Replacing Geb with G00 in the above CALL_VN.

  return loose_intro;
}

char* loose_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int loose_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int loose_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int loose_get_self_object_num() {
  return 34;
}

int loose_get_moves() {
  return (((short) zmp[10392]) << 8) | zmp[10393]; // 10405
}

short loose_get_score() {
  return zmp[10391]; // 10415, 10417
}

int loose_max_score() {
  return 50;
}

int loose_get_num_world_objs() {
  return 178;
}

int loose_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int loose_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int loose_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void loose_clean_world_objs(zobject* objs) {
  for (int i=1; i<=loose_get_num_world_objs(); ++i) {
    if (i != 99 && i != 101) {  // Except for 'knock' and 'ladder'.
      clear_attr(&objs[i], 8);
    }

    clear_attr(&objs[i], 25);
  }

  objs[176].parent = 0;
  clear_attr(&objs[176], 3);

  clear_prop(&objs[170], 41);  // Mary's counter.
  clear_prop(&objs[125], 41);  // Clock Tower's counter.
  clear_prop(&objs[174], 41);  // Mother Loose's counter.
}
