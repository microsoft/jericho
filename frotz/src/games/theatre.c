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

// Theatre: http://ifdb.tads.org/viewgame?id=bv8of8y9xeo7307g

const char *theatre_intro[] = { "\n" };

zword* theatre_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** theatre_intro_actions(int *n) {
  *n = 1;
  return theatre_intro;
}

char* theatre_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int theatre_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int theatre_game_over() {
  char *death_text = "*** You have died ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int theatre_get_self_object_num() {
  return 15;
}

int theatre_get_moves() {
  return (((short) zmp[17579]) << 8) | zmp[17580]; //17590
}

short theatre_get_score() {
  return (((short) zmp[17577]) << 8) | zmp[17578]; //17588, 17604
}

int theatre_max_score() {
  return 50;
}

int theatre_get_num_world_objs() {
  return 255;
}

int theatre_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int theatre_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 27)
    return 1;
  return 0;
}

int theatre_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 27)
    return 1;
  return 0;
}

void theatre_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 5) & ~(1 << 4);
    // Clear attr 26 & 27
    for (i=1; i<=theatre_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
