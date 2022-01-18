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

// Anchorhead: http://ifdb.tads.org/viewgame?id=op0uw1gn1tjqmjt7

const char *anchor_intro[] = { "\n", "\n", "\n" };

const zword anchor_special_ram_addrs[3] = {
  // 21922, // Combination lock
  40660, // Bathe
  // 38470, // Transitions between days
  // 37992, // Sleep
  8810, // Talking to Micheal
  // 18081, // Asking Bum about brother
  // 24928, // Turn c, w, h and e.
  18839, // Being chased by a monster around the Old Stone Well.
  // 31625, // Breaking door leading to Hallway.
  // 17267, // Ritual sequence in town square
  // 27970, // Opening the hatch and waiting for the sound.
};

zword* anchor_ram_addrs(int *n) {
    *n = 3;
    return anchor_special_ram_addrs;
}

char** anchor_intro_actions(int *n) {
  *n = 3;
  return anchor_intro;
}

char* anchor_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int anchor_victory() {
  //char *death_text = "****  You have won  ****";
  char *death_text = "*** You have won... for now ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int anchor_game_over() {
  char *death_text = "Do you want me to try to reincarnate you?";
  char *death_text2 = "Would you like to RESTART, RESTORE a saved game, UNDO";
  if (strstr(world, death_text) || strstr(world, death_text2)) {
    return 1;
  }
  return 0;
}

int anchor_get_self_object_num() {
  return 20;
}

int anchor_get_moves() {
  return (((short) zmp[37999]) << 8) | zmp[38000]; //38012
}

short anchor_get_score() {
  return zmp[38024]; //37998, 38022
}

int anchor_max_score() {
  return 100;
}

int anchor_get_num_world_objs() {
  return 764;
}

int anchor_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int anchor_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int anchor_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void anchor_clean_world_objs(zobject* objs) {
  // Zero out attribute 25 for all objects.
  // attr[0]  attr[1]  attr[2]  attr[3]
  // 11111111 01111111 11111111 10111111
  char mask3 = 0b10111111;  // Attr 25.
  for (int i=1; i<=anchor_get_num_world_objs(); ++i) {
      // objs[i].attr[1] &= mask1;
      objs[i].attr[3] &= mask3;
  }

  // Train's location according to its schedule.
  objs[141].parent = 0;

  char maskAttr8 = 0b01111111;  // Attr 8
  // Zero out Attr8 of the handcuffs.
  objs[518].attr[1] &= maskAttr8;

  int N;
  // Zero out the Wine Cellar's counter.
  N = 5;  // Prop40.
  memset(&objs[395].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[395].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Flashlight's battery counter.
  N = 5;  // Prop41.
  memset(&objs[370].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[370].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the pale, frightened woman's counter before she slams the door shut.
  N = 3;  // Prop40.
  memset(&objs[158].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[158].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the pressure gauge's counter controlling the noise it makes.
  N = 2;  // Prop41.
  memset(&objs[467].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[467].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the book of matches's counter before the match burns down completely.
  N = 4;  // Prop40.
  memset(&objs[372].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[372].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the metal handle's counter before its snaps back to an upright position.
  N = 2;  // Prop41.
  memset(&objs[472].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[472].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Island of Flesh's counter.
  N = 3;  // Prop41.
  memset(&objs[516].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[516].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the rain's counter controlling lighting.
  N = 4;  // Prop41.
  memset(&objs[82].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[82].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the madman's counter.
  N = 4;  // Prop41.
  memset(&objs[578].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[578].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Town Square's counter controlling the old man's faith.
  N = 3;  // Prop41.
  memset(&objs[172].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[172].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the (appearance)'s counter.
  N = 1;  // Prop41.
  memset(&objs[27].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[27].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the monster's counter.
  N = 3;  // Prop41.
  memset(&objs[171].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[171].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Lighthouse's counter controlling Michael's actions.
  N = 3;  // Prop41.
  memset(&objs[509].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[509].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Burial Mound's counter.
  N = 3;  // Prop40.
  memset(&objs[447].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[447].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the stone obelisk's counter.
  N = 2;  // Prop41.
  memset(&objs[174].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[174].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out Michael's counter.
  N = 4;  // Prop41.
  memset(&objs[524].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[524].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out ghost of Croseus Verlac's counter.
  N = 2;  // Prop41.
  memset(&objs[462].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[462].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out Home's counter.
  N = 2;  // Prop41.
  memset(&objs[231].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[231].prop_lengths[N-1] * sizeof(zbyte));

}
