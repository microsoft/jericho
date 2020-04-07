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

// Hollywood Hijinx: http://ifdb.tads.org/viewgame?id=jnfkbgdgopwfqist

const char *hollywood_intro[] = { "turn statue west\n",
                                  "turn statue east\n",
                                  "turn statue north\n" };

zword* hollywood_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** hollywood_intro_actions(int *n) {
  *n = 3;
  return hollywood_intro;
}

char* hollywood_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int hollywood_victory() {
  char *death_text = "Your score is 150 points out of 150";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hollywood_game_over() {
  char *death_text = "(Please type RESTART, RESTORE or QUIT.)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hollywood_get_self_object_num() {
  return 50;
}

int hollywood_get_moves() {
  return (((short) zmp[8194]) << 8) | zmp[8195];
}

short hollywood_get_score() {
  return zmp[8193];
}

int hollywood_max_score() {
  return 150;
}

int hollywood_get_num_world_objs() {
  return 239;
}

int hollywood_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int hollywood_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 50 && attr_idx == 23)
    return 1;
  return 0;
}

int hollywood_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (obj_num == 50 && attr_idx == 23)
    return 1;
  return 0;
}

void hollywood_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 3);
    // Clear attr 28
    for (i=1; i<=hollywood_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
