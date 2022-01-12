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

const zword curses_special_ram_addrs[20] = {
  786, 800, 828, 842, 856, 870, 884, 898, 926, // Interacting with the rods.
  // 1469, // Clean glass ball
  23711, // get High Rod of Love (warning message)
  23655, 23657, // Hole
  23673, 23675, // Maze navigation
  // 13293, // Revolving door
  // 23663, // Tarot cards
  25304, 23695, // Solving the sliding puzzle
  // 15147, // Talking to Homer
  23681, 23683, // Pacing
  // 14201, // Set timer
  // 20911, // Turn sceptre
  23701, // Close the lid.
  23707, // Lost inside the Palace
};

const char *curses_intro[] = { "\n" };

zword* curses_ram_addrs(int *n) {
    *n = 20;
    return curses_special_ram_addrs;
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
  // return 550;
  // Due to a bug, the max score is 554 points instead of 550.
  // ref: https://raw.githubusercontent.com/heasm66/walkthroughs/main/curses_walkthrough.txt
  return 554;
}

int curses_get_num_world_objs() {
  return 502;
}

int curses_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int curses_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)// || attr_idx == 8)
    return 1;
  return 0;
}

int curses_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (attr_idx == 25)// || attr_idx == 8)
    return 1;
  return 0;
}

void curses_clean_world_objs(zobject* objs) {
  // Zero out attribute 25 for all objects.
  // attr[0]  attr[1]  attr[2]  attr[3]
  // 11111111 11111111 11111111 10111111
  char mask3 = 0b10111111;  // Attr 25.
  for (int i=1; i<=curses_get_num_world_objs(); ++i) {
      objs[i].attr[3] &= mask3;
  }

  int N;
  // Zero out the antiquated wireless' counter.
  N = 2;  // Prop23.
  memset(&objs[111].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[111].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the glass cabinet' alarm counter.
  N = 2;  // Prop23.
  memset(&objs[200].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[200].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the Coven Cell's sacrifice counter.
  N = 3;  // Prop23.
  memset(&objs[195].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[195].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the "beanle"'s counter before avalanche of stones.
  N = 4;  // Prop23.
  memset(&objs[309].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[309].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the complicated-look bomb's counter.
  N = 3;  // Prop23.
  memset(&objs[205].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[205].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out the time-detonator's counter.
  N = 5;  // Prop23.
  memset(&objs[206].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[206].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out Causeway's counter that controls Austin (the cat) reactions.
  N = 3;  // Prop23.
  memset(&objs[396].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[396].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out BirdcagfMuses's counter until messenger-boy arrives.
  N = 3;  // Prop23.
  memset(&objs[448].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[448].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out Buried Alive's counter until the player suffocates.
  N = 3;  // Prop23.
  memset(&objs[431].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[431].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out tentle's counter before Saxon spy arrives.
  N = 3;  // Prop23.
  memset(&objs[353].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[353].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out unconscious Saxon spy's counter before the guards takes the spy away.
  N = 2;  // Prop23.
  memset(&objs[354].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[354].prop_lengths[N-1] * sizeof(zbyte));

  // Zero out Encampment's counter before one of the druids sees you.
  N = 3;  // Prop23.
  memset(&objs[355].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH], 0, objs[355].prop_lengths[N-1] * sizeof(zbyte));
}
