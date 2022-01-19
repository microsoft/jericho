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

// Ballyhoo: http://ifdb.tads.org/viewgame?id=b0i6bx7g4rkrekgg

const zword ballyhoo_special_ram_addrs[22] = {
  8853, // Listen to the conversation with Munrab.
  8623, // Crossing the tightrope
  9113, // turnstile
  8835, // Lion stand
  8723, // Give case to harry
  8639, // give money to hawker to buy candy
  8791, // stand
  8893, // walking in the crowd
  9053, // get out of line
  8539, // tina
  8911, // radio
  8643, // tape
  9047, // radio on/off
  // 8629, // search desk
  8759, // cards
  8989, // ladder
  2735, // veil
  1691, // dress
  8905, // mahler
  8543, // tightrope
  8545, // wpdl
  8845, // read the spreadsheet
  8525, // say hello Eddit to Chuckles.
};

zword* ballyhoo_ram_addrs(int *n) {
    *n = 22;
    return ballyhoo_special_ram_addrs;
}

char** ballyhoo_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* ballyhoo_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int ballyhoo_victory() {
  char *death_text = "having saved The Traveling Circus That Time Forgot, Inc.";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ballyhoo_game_over() {
  char *death_text = "(Type RESTART, RESTORE, or QUIT)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int ballyhoo_get_self_object_num() {
  return 211;
}

int ballyhoo_get_moves() {
  return (((short) zmp[8496]) << 8) | zmp[8497];
}

short ballyhoo_get_score() {
  return zmp[8495];
}

int ballyhoo_max_score() {
  return 200;
}

int ballyhoo_get_num_world_objs() {
  return 239;
}

int ballyhoo_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int ballyhoo_ignore_attr_diff(zword obj_num, zword attr_idx) {
  // if (obj_num == 211 && attr_idx == 13)
  // if (obj_num == 211)
    // return 1;
  if (attr_idx == 30)
    return 1;
  return 0;
}

int ballyhoo_ignore_attr_clr(zword obj_num, zword attr_idx) {
  // if (obj_num == 211)
    // return 1;
  if (attr_idx == 20)  // TODO: Should it be attr 30 like in ballyhoo_ignore_attr_diff ?
    return 1;
  return 0;
}

void ballyhoo_clean_world_objs(zobject* objs) {
  // Clear Attr30 for all objects.
  for (int i=1; i<=ballyhoo_get_num_world_objs(); ++i) {
      clear_attr(&objs[i], 30);
  }

  clear_attr(&objs[211], 13);  // it
  clear_attr(&objs[175], 18);  // Menagerie
  clear_attr(&objs[142], 12);  // concessistand

  // Ignore Chuckles (the clown) movements.
  objs[113].parent = 0;

  // Ignore hawker movements.
  objs[78].parent = 0;

}
