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

// Sherlock: http://ifdb.tads.org/viewgame?id=ug3qu521hze8bsvz

const char *sherlock_intro[] = { "\n" };

zword* sherlock_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** sherlock_intro_actions(int *n) {
  *n = 1;
  return sherlock_intro;
}

char* sherlock_clean_observation(char* obs) {
  return obs;
}

int sherlock_victory() {
  char *death_text = "Once again, Mr Holmes, we find ourselves in your debt.";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int sherlock_game_over() {
  char *death_text = "The game is no longer afoot";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int sherlock_get_self_object_num() {
  return 232;
}

int sherlock_get_moves() {
  return (((short) zmp[1002]) << 8) | zmp[1003];
}

short sherlock_get_score() {
  return zmp[739]; //993
}

int sherlock_max_score() {
  return 100;
}

int sherlock_get_num_world_objs() {
  return 314;
}

int sherlock_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int sherlock_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int sherlock_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void sherlock_clean_world_objs(zobject* objs) {
}
