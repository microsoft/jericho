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

// Hollywood Hijinx: http://ifdb.tads.org/viewgame?id=jnfkbgdgopwfqist

const zword hollywood_special_ram_addrs[8] = {
  8241, 8341, // Atomic Chihuahua
  8323, // Breathing fire
  8381, // Safe dial (Hallway)
  8345, // Push piano
  8269, // Hedge Maze
  8221, // Safe dial (Bomb Shelter)
  8363, // throw club at herman
};

const char *hollywood_intro[] = { "turn statue west\n",
                                  "turn statue east\n",
                                  "turn statue north\n" };

zword* hollywood_ram_addrs(int *n) {
    *n = 8;
    return hollywood_special_ram_addrs;
}

char** hollywood_intro_actions(int *n) {
  *n = 3;
  // Patch bug in source file.
  // 8b31:  GET_PROP        G00,#0c -> -(SP)
  // 8b35:  PRINT_PADDR     (SP)+
  //
  // G00 is object 102 (Crawl Space, South) which doesn't have property 0x0c (i.e., 12).
  // PRINT_PADDR will try to print text found at address 0 (segfault).
  // Replace that PRINT_PADDR op with the nop.
  zmp[0x8b35] = 180;  // Nop
  zmp[0x8b36] = 180;  // Nop

  return hollywood_intro;
}

char* hollywood_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int hollywood_victory() {
  char *death_text = "Your score is 150 points out of 150";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hollywood_game_over() {
  char *death_text = "(Please type RESTART, RESTORE or QUIT.)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hollywood_get_self_object_num() {
  return 50;
}

int hollywood_get_moves() {
  return (((short) zmp[8194]) << 8) | zmp[8195];
}

short hollywood_get_score() {
  return zmp[8193];
}

int hollywood_max_score() {
  return 150;
}

int hollywood_get_num_world_objs() {
  return 239;
}

int hollywood_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int hollywood_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 50 && attr_idx == 23)
    return 1;
  return 0;
}

int hollywood_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (obj_num == 50 && attr_idx == 23)
    return 1;
  return 0;
}

void hollywood_clean_world_objs(zobject* objs) {
  for (int i=1; i<=hollywood_get_num_world_objs(); ++i) {
    clear_attr(&objs[i], 4);
    clear_attr(&objs[i], 28);
  }

  clear_attr(&objs[116], 31);  // Upstairs Hall
  clear_attr(&objs[158], 31);  // Entrance to Hedge Maze

  clear_prop(&objs[19], 1);  // Red match counter.
  clear_prop(&objs[169], 1);  // Green match counter.
  clear_prop(&objs[181], 9);  // The red wax statuette burning down counter.

  // Completely ignore the 'pseudo' object.
  strcpy(&objs[237].name, "pseudo");  // Its name reflects what the player's focus.
  clear_prop(&objs[237], 31);
}
