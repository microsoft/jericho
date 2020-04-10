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


#include <stdlib.h>
#include <string.h>
#include "frotz.h"
#include "games.h"
#include "frotz_interface.h"

// Games generated with TextWorld: https://github.com/Microsoft/TextWorld

int tw_num_world_objs = 0;
int tw_player_obj_num = 0;
int move_count = 0;
int tw_score = 0;
int tw_max_score = 0;

// Reverse search a given char in a string.
char* strchr_rev(char* start, char* end, char c) {
  while (end >= start && *end != c) {
    end = end - 1;
  }
  if (*end != c) {
    end = NULL;
  }

  return end;
}

// Parse the move count from the world observation; Eg -= Studio =-0/4 --> 0 and 4
void parse_score_and_move_count(char* obs) {
  char* pch = obs;
  char* last;
  while (pch != NULL) {
    last = pch;
    pch = strchr(pch+1, '/');
  }
  if (last != NULL) {
    pch = strchr_rev(obs, last, '-');
    if (pch) {
      tw_score = strtol(pch+1, NULL, 10);
    }
    move_count = strtol(last+1, &last, 10);
  }
}

zword* textworld_ram_addrs(int *n) {
    *n = 0;
    return NULL;
}

char** textworld_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* textworld_clean_observation(char* obs) {
  char* pch;
  parse_score_and_move_count(obs);
  pch = strrchr(obs, '>');
  if (pch != NULL) {
    *(pch-1) = '\0';
  }
  return obs+1;
}

int textworld_victory() {
  char *death_text = "*** The End ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int textworld_game_over() {
  char *death_text = "*** You lost! ***";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int textworld_get_self_object_num() {
  return tw_player_obj_num;
}

int textworld_get_moves() {
  return move_count;
}

short textworld_get_score() {
  if (textworld_victory())
    return tw_max_score;
  return tw_score;
}

int textworld_max_score() {
  return tw_max_score;
}

int textworld_get_num_world_objs() {
  return tw_num_world_objs;
}

int textworld_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int textworld_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 35 || attr_idx == 31)
    return 1;
  return 0;
}

int textworld_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 35 || attr_idx == 31)
    return 1;
  return 0;
}

void textworld_clean_world_objs(zobject* objs) {
}
