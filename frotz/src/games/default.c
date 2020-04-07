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

zword* default_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** default_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* default_clean_observation(char* obs) {
  return obs;
}

int default_victory() {
  char *death_text = "****  You have won  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int default_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int default_get_self_object_num() {
  return 20;
}

int default_get_moves() {
  return 0;
}

short default_get_score() {
  return 0;
}

int default_max_score() {
  return 0;
}

int default_get_num_world_objs() {
  return 0;
}

int default_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int default_ignore_attr_diff(zword obj_num, zword attr_idx) {
  return 0;
}

int default_ignore_attr_clr(zword obj_num, zword attr_idx) {
  return 0;
}

void default_clean_world_objs(zobject* objs) {
}
