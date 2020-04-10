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

// Deephome: A Telleen Adventure: http://ifdb.tads.org/viewgame?id=x85otcikhwp8bwup

zword* deephome_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** deephome_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* deephome_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int deephome_victory() {
  char *death_text = "****  You have won  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int deephome_game_over() {
  char *death_text = "Would you like to RESTART, RESTORE a saved game, give the FULL score for that game or QUIT";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int deephome_get_self_object_num() {
  return 20;
}

int deephome_get_moves() {
  return (((short) zmp[12411]) << 8) | zmp[12412]; // 12424
}

short deephome_get_score() {
  return (((short) zmp[12433]) << 8) | zmp[12434]; // 12436, 12410: 1.0
}

int deephome_max_score() {
  return 300;
}

int deephome_get_num_world_objs() {
  return 255;
}

int deephome_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int deephome_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 29)
    return 1;
  return 0;
}

int deephome_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 29)
    return 1;
  return 0;
}

void deephome_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 3) & ~(1 << 2);
    // Clear attr 28 & 29
    for (i=1; i<=deephome_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
