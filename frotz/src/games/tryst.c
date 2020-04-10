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

// Tryst of Fate: http://ifdb.tads.org/viewgame?id=ic0ebhbi70bdmyc2

const char *tryst_intro[] = { "\n" };

zword* tryst_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** tryst_intro_actions(int *n) {
  *n = 1;
  return tryst_intro;
}

char* tryst_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int tryst_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int tryst_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int tryst_get_self_object_num() {
  return 20;
}

int tryst_get_moves() {
  return (((short) zmp[15262]) << 8) | zmp[15263]; //15275
}

short tryst_get_score() {
  return (((short) zmp[15260]) << 8) | zmp[15261]; //15285, 15287
}

int tryst_max_score() {
  return 350;
}

int tryst_get_num_world_objs() {
  return 255;
}

int tryst_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int tryst_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int tryst_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void tryst_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 7);
    // Clear attr 24
    for (i=1; i<=tryst_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
