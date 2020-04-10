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

// Escape from the Starship Zenon: http://ifdb.tads.org/viewgame?id=rw7zv98mifbr3335

zword* zenon_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** zenon_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* zenon_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int zenon_victory() {
  char *victory_text = "*** You have won ***";
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int zenon_game_over() {
  char *death_text = "****  You have died  ****";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int zenon_get_self_object_num() {
  return 20;
}

int zenon_get_moves() {
  return (((short) zmp[3743]) << 8) | zmp[3744]; //3756
}

short zenon_get_score() {
  return (((short) zmp[3741]) << 8) | zmp[3742]; //3766, 3768
}

int zenon_max_score() {
  return 20;
}

int zenon_get_num_world_objs() {
  return 74;
}

int zenon_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int zenon_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int zenon_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void zenon_clean_world_objs(zobject* objs) {
    char mask;
    int i;
    zobject* janitor_obj;
    zobject* janitor_loc;
    janitor_obj = &objs[34];
    janitor_loc = &objs[janitor_obj->parent];
    if (janitor_loc->child == 34) {
        janitor_loc->child = janitor_obj->sibling;
    }
    janitor_obj->parent = 0;
    janitor_obj->sibling = 0;
    janitor_obj->child = 0;
    mask = ~(1 << 7);
    // Clear attr 24
    for (i=1; i<=zenon_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
