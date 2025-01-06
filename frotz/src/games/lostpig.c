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

// Lost Pig: http://ifdb.tads.org/viewgame?id=mohwfk47yjzii14w

const zword lostpig_special_ram_addrs[0] = {
  // 13958, // Looking for pig.
  // 2757, // Coin in box.
  // 2795, // Have chair
  // 2921, // Acquiring book
  // 2575, // Fill hat with water
  // 2846, // Chest open
  // 2895, // Picking up, dropping various objects
};

zword* lostpig_ram_addrs(int *n) {
    *n = 0;
    return lostpig_special_ram_addrs;
}

char** lostpig_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* lostpig_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '>');
  if (pch != NULL) {
    *(pch-2) = '\0';
  }
  return obs+1;
}

int lostpig_victory() {
  // Winning messages change depending on the score.
  // ***  Grunk bring pig back to farm ***  // 6 out of 7 points.
  // ***  Grunk bring pig back to farm and make new friend ***  // 7 out of 7 points.
  char *victory_text = "***  Grunk bring pig back to farm ";  // Works for both 6 and 7 points.
  if (strstr(world, victory_text)) {
    return 1;
  }
  return 0;
}

int lostpig_game_over() {
  char *death_text = "Time for Grunk to RESTART or RESTORE a saved story or UNDO";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int lostpig_get_self_object_num() {
  return 87;
}

int lostpig_get_moves() {
  return (((short) zmp[39582]) << 8) | zmp[39583]; // 39607
}

short lostpig_get_score() {
  return zmp[39581]; //39617, 39619
}

int lostpig_max_score() {
  return 7;
}

int lostpig_get_num_world_objs() {
  return 535;
}

int lostpig_ignore_moved_obj(zword obj_num, zword dest_num) {
  if (obj_num != 87 && dest_num != 87)
    return 1;
  return 0;
}

int lostpig_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (attr_idx == 14 || attr_idx == 15)
    return 1;
  return 0;
}

int lostpig_ignore_attr_clr(zword obj_num, zword attr_idx) {
  /* if (attr_idx == 14 || attr_idx == 15) */
  return 1;
  /* return 0; */
}

void lostpig_clean_world_objs(zobject* objs) {
  clear_attr(&objs[161], 1);  // (chestPowder)
  clear_attr(&objs[210], 20);  // box
  clear_attr(&objs[161], 15);  // (chestPowder)

  for (int i=1; i<=lostpig_get_num_world_objs(); ++i) {
    clear_attr(&objs[i], 31);
    if (i != 201) {  // Skip ball.
      clear_attr(&objs[i], 14);
    }

    if (i != 183 && i != 98) {  // Skip (maze) and noise.
      clear_prop(&objs[i], 54);  // object's counter (if any)
    }
  }

  clear_prop(&objs[98], 53);  // noise's counter
  clear_prop(&objs[210], 8);  // box's description?
  clear_prop(&objs[210], 1);  // box's description?
  clear_prop(&objs[194], 9);  // (gRoom)

  objs[211].parent = 0;  // trfustuff
  objs[293].parent = 0;  // wlfor
  objs[127].parent = 0;  // pig
  objs[528].parent = 0;  // (bH)
  objs[208].parent = 0;  // smoke
  objs[388].parent = 0;  // b (topic)

  objs[206].parent = 0;  // pipe
  objs[207].parent = 0;  // bag

  objs[209].parent = 0;  // strange helmet
  objs[210].parent = 0;  // box
  objs[404].parent = 0;  // looter
  objs[385].parent = 0;  // tool (topic)
  objs[386].parent = 0;  // strange helmet (topic)

  objs[426].parent = 0;  // misspage (topic)
  objs[453].parent = 0;  // propaper (topic)
  objs[529].parent = 0;  // (pageH) (topic)

  objs[329].parent = 0;  // stuff tray
  objs[361].parent = 0;  // pretty picture (topic)
}
