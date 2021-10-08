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

// Cutthroats: http://ifdb.tads.org/viewgame?id=4ao65o1u0xuvj8jf
const zword cutthroat_special_ram_addrs[7] = {
  8785, // Lock state of bedroom door.
  8669, 9021, // Answering Johnny's questions.
  10635,  // Waiting for McGinty to leave.
  8845, 8847,  // Tell longitude and latitude to Johnny.
  8987, // Track most of the game progression. Needed for "Fill tank with air".
};

zword* cutthroat_ram_addrs(int *n) {
    *n = 7;
    return cutthroat_special_ram_addrs;
}

char** cutthroat_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* cutthroat_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int cutthroat_victory() {
  char *death_text = "Good job, matey!";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int cutthroat_game_over() {
  char *death_text = "RESTART, RESTORE, or QUIT";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int cutthroat_get_self_object_num() {
  return 184;
}

int cutthroat_get_moves() {
  return (((short) zmp[8644]) << 8) | zmp[8645]; //9041
}

short cutthroat_get_score() {
  return zmp[8871]; //8873
}

int cutthroat_max_score() {
  return 250;
}

int cutthroat_get_num_world_objs() {
  return 223;
}

int cutthroat_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int cutthroat_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int cutthroat_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void cutthroat_clean_world_objs(zobject* objs) {
    zobject *weasel_obj, *weasel_loc;
    zobject *player_obj, *player_loc;

    player_obj = &objs[184];
    player_loc = &objs[player_obj->parent];
    weasel_obj = &objs[9];
    weasel_loc = &objs[weasel_obj->parent];

    // Filter out Weasel when not in sight.
    if (player_loc->num != weasel_loc->num) {
      if (weasel_loc->child == 9) {
          weasel_loc->child = weasel_obj->sibling;
      }

      weasel_obj->parent = 0;
      weasel_obj->sibling = 0;
      weasel_obj->child = 0;
    }
}
