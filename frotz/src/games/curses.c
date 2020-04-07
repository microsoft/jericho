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

// Curses: http://ifdb.tads.org/viewgame?id=plvzam05bmz3enh8

const char *curses_intro[] = { "\n" };

zword* curses_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** curses_intro_actions(int *n) {
  *n = 1;
  return curses_intro;
}

char* curses_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int curses_victory() {
  char *death_text = "*** You have won ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int curses_game_over() {
  char *death_text = "Would you like to RESTART";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int curses_get_self_object_num() {
  return 15;
}

int curses_get_moves() {
  return (((short) zmp[23374]) << 8) | zmp[23375]; // Also 23385
}

short curses_get_score() {
  return (((short) zmp[23372]) << 8) | zmp[23373]; // Also 23383 23399
}

int curses_max_score() {
  return 550;
}

int curses_get_num_world_objs() {
  return 255;
}

int curses_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int curses_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

int curses_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)
    return 1;
  return 0;
}

void curses_clean_world_objs(zobject* objs) {
    int i;
    char mask;
    mask = ~(1 << 7);
    // Clear attr 24
    for (i=1; i<=curses_get_num_world_objs(); ++i) {
        objs[i].attr[3] &= mask;
    }
}
