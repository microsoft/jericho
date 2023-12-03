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

// Monsters of Murdac: http://ifdb.tads.org/viewgame?id=q36lh5np0q9nak28

const zword murdac_special_ram_addrs[1] = {
  // 3909,  // Blow shawm; Also 525
  // 3587,  // Tracks state of door. Also 3626
  // 4659,  // Tracks throwing plank, rod.
  // 637,   // Scare centaur with blow shawm
  // 2934,  // Eat toadstone
  // 5838,  // Wave scroll, dig;
  // 3042,  // Tracks lion health
  // 2548,  // Fill bowl, look
  // 3365,  // Prick dummy, exodus
  6387,  // Running away from the poltergeist.
};

zword* murdac_ram_addrs(int *n) {
    *n = 1;
    return murdac_special_ram_addrs;
}

char** murdac_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* murdac_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch) = '\0';
  }
  return obs+1;
}

int murdac_victory() {
  char *victory_text = "are taken off in triumph to the land of Heroes of Murdac";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int murdac_game_over() {
  char *death_text = "Another game, your Extravagance?";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int murdac_get_self_object_num() {
  return 7;
}

int murdac_get_moves() {
  return (((short) zmp[6372]) << 8) | zmp[6373]; //6375,6383
}

short murdac_get_score() {
  // Reaching victory is actually worth 1 point but the game
  //  terminates before increasing the score. So, we do it manually.
  if (murdac_victory())
    return 250;

  return zmp[6357];
}

int murdac_max_score() {
  return 250;
}

int murdac_get_num_world_objs() {
  return 126;
}

int murdac_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int murdac_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 1)
    return 1;
  return 0;
}

int murdac_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 1)
    return 1;
  return 0;
}

void murdac_clean_world_objs(zobject* objs) {
  clear_attr(&objs[15], 5);  // (MONSTER)
  clear_prop(&objs[10], 4);  // (OGRE)
  clear_prop(&objs[62], 4);  // (WALL1)
  clear_prop(&objs[104], 4);  // (MONKROOM)
  clear_prop(&objs[90], 4);  // (BEACH3)
  clear_prop(&objs[119], 4);  // (ISLE1)
}
