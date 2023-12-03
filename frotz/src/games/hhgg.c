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

// Hitchhiker's Guide to the Galaxy: http://ifdb.tads.org/viewgame?id=ouv80gvsl32xlion

const zword hhgg_special_ram_addrs[18] = {
  8767, // Lie down in front of bulldozer
  8189, // Wait on bulldozer
  8169, // Beer
  8333, // Access Improbability Drive
  8115, // Beast
  8325, // Put bit in tea
  8053, // Sensations
  8087, // Autopilot
  8091, // Steering
  8171, // give towel to Arthur
  8185, // Walk around bulldozer
  8187, // Prossner lie in the mud
  8041, // no tea
  8349, // Marvin, open hatch
  8119, // Enjoy poetry.
  8105, // Spongy gray maze
  8327, // Put small plug in plotter
  2428, // Put large plug in large receptacle
};

zword* hhgg_ram_addrs(int *n) {
    *n = 18;
    return hhgg_special_ram_addrs;
}

char** hhgg_intro_actions(int *n) {
  *n = 0;
  return NULL;
}

char* hhgg_clean_observation(char* obs) {
  char* pch;
  pch = strchr(obs, '\n');
  if (pch != NULL) {
    return pch+1;
  }
  return obs;
}

int hhgg_victory() {
  char *death_text = "You step onto the landing ramp";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hhgg_game_over() {
  char *death_text = "(Type RESTART, RESTORE, or QUIT)";
  if (strstr(world, death_text)) {
    return 1;
  }
  return 0;
}

int hhgg_get_self_object_num() {
  return 31;
}

int hhgg_get_moves() {
  return (((short) zmp[7912]) << 8) | zmp[7913];
}

short hhgg_get_score() {
  return (((short) zmp[7910]) << 8) | zmp[7911];
}

int hhgg_max_score() {
  return 400;
}

int hhgg_get_num_world_objs() {
  return 220;
}

int hhgg_ignore_moved_obj(zword obj_num, zword dest_num) {
  return 0;
}

int hhgg_ignore_attr_diff(zword obj_num, zword attr_idx) {
  if (obj_num == 31 && attr_idx == 17)
    return 1;
  return 0;
}

int hhgg_ignore_attr_clr(zword obj_num, zword attr_idx) {
  if (obj_num == 31 && attr_idx == 17)
    return 1;
  return 0;
}

void hhgg_clean_world_objs(zobject* objs) {
  clear_attr(&objs[31], 17);  // it
  clear_attr(&objs[166], 6);  // bulldozer
  clear_attr(&objs[135], 5);  // dog
  clear_attr(&objs[70], 5);  // hostess

  // objs[156].parent = 0;  // thing aunt gave know is
  objs[215].parent = 0;  // Marvin

  for (int i=1; i<=hhgg_get_num_world_objs(); ++i) {
    if (i != 127) {
      clear_attr(&objs[i], 25);
      clear_attr(&objs[i], 27);
    }
  }

  // Completely ignore the 'pseudo' object.
  strcpy(&objs[48].name, "pseudo");  // Its name reflects what the player's focus.
  clear_prop(&objs[48], 29);


  // Track whether the Nutrimat has been activated.
  int N = 23;  // Use last property slot.
  objs[209].prop_ids[N-1] = 63;
  objs[209].prop_lengths[N-1] = 1;
  objs[209].prop_data[(N-1) * JERICHO_PROPERTY_LENGTH] = (zmp[8339] > 0);
}
