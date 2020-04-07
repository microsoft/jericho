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

// All Quiet on the Library Front: http://ifdb.tads.org/viewgame?id=400zakqderzjnu1i

const char *library_intro[] = { "\n" };

zword* library_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** library_intro_actions(int *n) {
  *n = 1;
  return library_intro;
}

char* library_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int library_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int library_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int library_get_self_object_num() {
  return 15;
}

int library_get_moves() {
  return (((short) zmp[3611]) << 8) | zmp[3612];
}

short library_get_score() {
  return zmp[3610]; //3626
}

int library_max_score() {
  return 30;
}

int library_get_num_world_objs() {
  return 76;
}

int library_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int library_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int library_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void library_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 7) & ~(1 << 6);
    // Clear attr 24 & 25
    for (i=1; i<=library_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
