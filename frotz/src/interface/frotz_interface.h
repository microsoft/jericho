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


#ifndef frotz_interface_h__
#define frotz_interface_h__

typedef struct {
  unsigned int num;
  char name[64];
  int parent;
  int sibling;
  int child;
  char attr[4];
  unsigned char properties[16];
} zobject;

extern char* setup(char *story_file, int seed, void* rom, size_t rom_size);

extern void shutdown();

extern char* step(char *next_action);

extern int save(char *filename);

extern int restore(char *filename);

extern int undo();

extern int getRAMSize();

extern void getRAM(unsigned char *ram);

extern char world[8192];

extern int tw_max_score;

extern int tw_player_obj_num;

extern int tw_num_world_objs;

#endif
