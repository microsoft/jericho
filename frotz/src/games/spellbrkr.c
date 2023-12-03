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

// Spellbreaker: http://ifdb.tads.org/viewgame?id=wqsmrahzozosu3r

const zword spellbrkr_special_ram_addrs[9] = {
  8987, // Notice the hole in the floor opens into thin air
  8737, // Falling + carried by huge bird
  8935, // Flying
  9007, //:   2 : 104.sleep(5), 247.sleep(6)
  8969, // Buying blue carpet.
  8961, // water level in channel.
  8857, // Move rock around.
  8997, // ask belboz about me (alt. 9111)
  8979, // Dialog with shadow.
};

zword* spellbrkr_ram_addrs(int *n) {
    *n = 9;
    return spellbrkr_special_ram_addrs;
}

char** spellbrkr_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* spellbrkr_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int spellbrkr_victory() {
  char *victory_text = "The age of magic is ended, as it must, for as magic can confer absolute power, so it can also produce absolute evil. We may defeat this evil when it appears, but if wizardry builds it anew, we can never ultimately win. The new world will be strange, but in time it will serve us better";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int spellbrkr_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int spellbrkr_get_self_object_num() {
  return 52;
}

int spellbrkr_get_moves() {
  return (((short) zmp[8726]) << 8) | zmp[8727];
}

short spellbrkr_get_score() {
  return (((short) zmp[8724]) << 8) | zmp[8725];
}

int spellbrkr_max_score() {
  return 600;
}

int spellbrkr_get_num_world_objs() {
  return 249;
}

int spellbrkr_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int spellbrkr_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int spellbrkr_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void spellbrkr_clean_world_objs(zobject* objs) {
}
