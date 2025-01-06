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
const zword cutthroat_special_ram_addrs[9] = {
  8785, // Lock state of bedroom door.
  // 8669, 9021, // Answering Johnny's questions.
  8922, // Deal with money.
  9021, // Answering Johnny's questions.
  // 10635,  // Waiting for McGinty to leave.
  8845, 8847,  // Tell longitude and latitude to Johnny.
  // 8775,  // Track amount of air in the air tank. (see cutthroat_clean_world_objs).
  9011,  // Hunger status.
  8771,  // Turn on magnet.
  8753,  // Turn drill on/off.
  8747,  // Track diving depth.
};

zword* cutthroat_ram_addrs(int *n) {
    *n = 9;
    return cutthroat_special_ram_addrs;
}

char** cutthroat_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* cutthroat_clean_observation(char* obs) {
  char* pch;
  pch = strrchr(obs, '>');
  if (pch != NULL) {
    *(pch) = '\0';
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

  clear_attr(&objs[184], 19);  // cretin, a.k.a. the player.
  clear_attr(&objs[9], 29);  // Weasel
  clear_attr(&objs[155], 30);  // ferry
  clear_attr(&objs[133], 30);  // envelope
  clear_attr(&objs[90], 30);  // Orange line
  clear_attr(&objs[33], 31);  // collectirstamps
  clear_attr(&objs[124], 31);  // C battery

  int N;
  // Zero out
  N = 1;  // Prop18.
  memset(&objs[217].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[217].prop_lengths[N-1] * sizeof(zbyte));
  N = 2;  // Prop17.
  memset(&objs[217].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[217].prop_lengths[N-1] * sizeof(zbyte));
  N = 3;  // Prop15.
  memset(&objs[217].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[217].prop_lengths[N-1] * sizeof(zbyte));

  objs[14].parent = 0;  // McGinty
  objs[12].parent = 0;  // Johnny Red
  objs[11].parent = 0;  // Rat
  objs[155].parent = 0;  // ferry
  objs[7].parent = 0;  // Merchant Seaman's card
  objs[5].parent = 0;  // Delivery boy
  objs[104].parent = 0;  // Delivery boy's cart?
  objs[105].parent = 0;  // meal
  objs[8].parent = 0;  // Weasel's knife
  objs[28].parent = 0;  // Orange line
  objs[90].parent = 0;  // Orange line

  // Track whether air tank has air in it.
  N = 23;
  objs[136].prop_ids[N-1] = 63;
  objs[136].prop_lengths[N-1] = 1;
  objs[136].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH] = (zmp[8775] > 0);
}
