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

// Party Foul - http://ifdb.tads.org/viewgame?id=cqwq699i9qiqdju

const zword partyfoul_special_ram_addrs[4] = {
  17509,  // Spread peanut butter on frank (alt. 17755, 19428, 21423, 47829)
  1923, // plug the toaster
  2259, // plug the hair dryer
  28036, // Waiting for your husband to be prepared to leave the party (alt. 28037, 32186)
};

const char *partyfoul_intro[] = { "\n", "no\n", "\n" };

zword* partyfoul_ram_addrs(int *n) {
    *n = 4;
    return partyfoul_special_ram_addrs;
}

char** partyfoul_intro_actions(int *n) {
  *n = 3;
  skip_z_read_char = TRUE;
  return partyfoul_intro;
}

char* partyfoul_clean_observation(char* obs) {
  char* pch;
  pch = strstr(obs, "> ");
  if (pch != NULL) {
    *(pch-1) = '\0';
  }
  return obs + strspn(obs, "\n ");  // Skip leading newlines and whitespaces.
}

int partyfoul_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int partyfoul_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int partyfoul_get_self_object_num() {
  return 48;
}

int partyfoul_get_moves() {
  return (((short) zmp[15810]) << 8) | zmp[15811];
}

short partyfoul_get_score() {
  if (partyfoul_victory()) {
    return 1;
  }
  return 0;
}

int partyfoul_max_score() {
  return 1;
}

int partyfoul_get_num_world_objs() {
  return 141;
}

int partyfoul_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int partyfoul_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 35 || attr_idx == 29)
    return 1;
  return 0;
}

int partyfoul_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 35)
    return 1;
  return 0;
}

void partyfoul_clean_world_objs(zobject* objs) {
  for (int i=1; i<=partyfoul_get_num_world_objs(); ++i) {
      clear_attr(&objs[i], 29);
      clear_attr(&objs[i], 30);
  }

  clear_attr(&objs[124], 21);

  objs[49].parent = 0;
  objs[67].parent = 0;
  objs[84].parent = 0;
  objs[85].parent = 0;
  objs[86].parent = 0;
  objs[95].parent = 0;
  objs[100].parent = 0;
}
