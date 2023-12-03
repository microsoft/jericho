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

// Plundered Hearts: http://ifdb.tads.org/viewgame?id=ddagftras22bnz8h

const zword plundered_special_ram_addrs[10] = {
  729, // Tracks how far you have climbed the ladder
  863, // Dip rag in water.
  687, // Interacting with Lafond.
  881, // Wait for Crulley to come back.
  889, // Hit Crulley with coffer
  1003, // Butler's falling asleep
  1071, // Dialog with Jamison
  1133, // In the cask, current pulling you.
  1143, // Crocodile falling asleep.
  9603, // Mast falls to the deck
};

const char *plundered_intro[] = { "\n" };

zword* plundered_ram_addrs(int *n) {
    *n = 10;
    return plundered_special_ram_addrs;
}

char** plundered_intro_actions(int *n) {
  *n = 1;
  return plundered_intro;
}

char* plundered_clean_observation(char* obs) {
  if (strstr(obs, ">SHOOT") != NULL){
    return obs;
  }

  return obs + strspn(obs, "> \n");  // Skip leading prompt, whitespaces, and newlines.
}

int plundered_victory() {
  char *death_text = "Thus you have finished the story of PLUNDERED HEARTS";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int plundered_game_over() {
  char *death_text = "***   You have died   ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int plundered_get_self_object_num() {
  return 192;
}

int plundered_get_moves() {
  return (((short) zmp[678]) << 8) | zmp[679];
}

short plundered_get_score() {
  return zmp[677];
}

int plundered_max_score() {
  return 25;
}

int plundered_get_num_world_objs() {
  return 223;
}

int plundered_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int plundered_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int plundered_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void plundered_clean_world_objs(zobject* objs) {
}
