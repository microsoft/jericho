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

// Seastalker: http://ifdb.tads.org/viewgame?id=56wb8hflec2isvzm

const char *seastalker_intro[] = { "John\n", "Wayne\n", "yes\n" };

zword* seastalker_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** seastalker_intro_actions(int *n) {
  *n = 3;
  return seastalker_intro;
}

char* seastalker_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int seastalker_victory() {
  char *victory_text = "CONGRATULATIONS, JOHN! YOU'VE COMPLETED YOUR MISSION!!";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int seastalker_game_over() {
  char *death_text = "RESTART the story from the beginning";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int seastalker_get_self_object_num() {
  return 191;
}

int seastalker_get_moves() {
  return (((short) zmp[9311]) << 8) | zmp[9312];
}

short seastalker_get_score() {
  return (char) zmp[9310];
}

int seastalker_max_score() {
  return 100;
}

int seastalker_get_num_world_objs() {
  return 249;
}

int seastalker_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int seastalker_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 6)
    return 1;
  return 0;
}

int seastalker_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 6)
    return 1;
  return 0;
}

void seastalker_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 1);
    // Clear attr 6
    for (i=1; i<=seastalker_get_num_world_objs(); ++i) {
        objs[i].attr[0] &= mask;
    }
}
