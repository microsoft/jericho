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
#include <stdio.h>
#include <errno.h>
#include "frotz.h"
#include "frotz_interface.h"
#include "games.h"
#include "ztools.h"
#include "md5.h"

extern void interpret (void);
extern void interpret_until_read (void);
extern void init_memory (void);
extern void init_undo (void);
extern void reset_memory (void);
extern zbyte get_next_opcode (void);
extern void run_opcode (zbyte opcode);
extern void dumb_set_next_action (char *a);
extern void dumb_show_screen (int a);
extern char* dumb_get_screen(void);
extern void dumb_clear_screen(void);
extern char* dumb_get_lower_screen(void);
extern void dumb_clear_lower_screen(void);
extern char* dumb_get_upper_screen(void);
extern void dumb_clear_upper_screen(void);
extern void z_save (void);
extern void load_story(char *s);
extern void load_story_rom(char *s, void* rom, size_t rom_size);
extern zword save_quetzal (FILE *, FILE *);
extern zword restore_quetzal (FILE *, FILE *);
extern int restore_undo (void);
extern void split_window (zword);
extern void erase_window (zword);
extern void restart_header (void);
extern zword object_name (zword);
extern zword object_address (zword);
extern zword get_parent (zword);
extern zword get_child (zword);
extern zword get_sibling (zword);
extern void insert_tree(zword obj1, zword obj2);
extern void insert_obj(zword obj1, zword obj2);
extern void seed_random (int value);
extern void set_random_seed (int seed);
extern void sum(FILE*, char*);
extern void dumb_free();

extern zword first_property (zword);
extern zword next_property (zword prop_addr);
extern void get_text(int, zword, char*);
extern void free_setup();

extern long getRngA();
extern int getRngInterval();
extern int getRngCounter();
extern void setRng(long, int, int);

zbyte next_opcode;
bool skip_z_read_char = FALSE;
int last_ret_pc = -1;
int desired_seed = 0;
int ROM_IDX = 0;

char world[256 + 8192] = "";  // Upper + lower screens.

int emulator_halted = 0;
char halted_message[] = "Emulator halted due to runtime error.\n";

// Track the objects.
zobject* prev_objs_state = NULL;
zobject* curr_objs_state = NULL;

// Track the value of special per-game ram locations.
zbyte* prev_special_ram = NULL;
zbyte* curr_special_ram = NULL;

bool objects_state_changed = FALSE;
bool special_ram_changed = FALSE;


// Runs a single opcode on the Z-Machine
void zstep() {
  run_opcode(next_opcode);
  next_opcode = get_next_opcode();
}

// Run the Z-Machine until it requires user input
void run_free() {
  // Opcode 228 (z_read) and 246 (z_read_char) indicate need for user input
  while (next_opcode != 228 && (next_opcode != 246 || skip_z_read_char) && emulator_halted <= 0) {
    zstep();
  }
}

void replace_newlines_with_spaces(char *s) {
  char* pch;
  for (;;) {
    pch = strchr(s, '\n');
    if (pch == NULL) {
      break;
    }
    *pch = ' ';
    s = pch;
  }
}

char* trim_whitespaces(char* obs) {
  // Trim trailing whitespace.
  char* pch = obs + strlen(obs) - 1;
  while (pch > obs && isspace(*pch)) {
      pch = pch - 1;
  }
  *(pch+1) = '\0';

  // Trim leading whitespaces.
  return obs + strspn(obs, "\n\r ");
}

enum SUPPORTED {
  DEFAULT_,
  ACORNCOURT_,
  ADVENTURELAND_,
  ADVENT_,
  AFFLICTED_,
  ANCHOR_,
  AWAKEN_,
  BALANCES_,
  BALLYHOO_,
  CURSES_,
  CUTTHROAT_,
  DEEPHOME_,
  DETECTIVE_,
  DRAGON_,
  ENCHANTER_,
  ENTER_,
  GOLD_,
  HHGG_,
  HOLLYWOOD_,
  HUNTDARK_,
  INFIDEL_,
  INHUMANE_,
  JEWEL_,
  KARN_,
  LIBRARY_,
  LOOSE_,
  LOSTPIG_,
  LUDICORP_,
  LURKING_,
  MOONLIT_,
  MURDAC_,
  NIGHT_,
  NINE05_,
  OMNIQUEST_,
  PARTYFOUL_,
  PENTARI_,
  PLANETFALL_,
  PLUNDERED_,
  REVERB_,
  SEASTALKER_,
  SHERBET_,
  SHERLOCK_,
  SNACKTIME_,
  SORCERER_,
  SPELLBRKR_,
  SPIRIT_,
  TEMPLE_,
  THEATRE_,
  TRINITY_,
  TRYST_,
  WEAPON_,
  WISHBRINGER_,
  YOMOMMA_,
  ZENON_,
  ZORK1_,
  ZORK2_,
  ZORK3_,
  ZTUU_,
  TEXTWORLD_
};

// Set ROM_IDX according to the story_file.
void load_rom_bindings(char *story_file) {
  char md5_hash[32];
  char *start;

  FILE * f = fopen (story_file, "r");
  if (f == NULL) {
    os_fatal(strerror(errno));
  }
  sum(f, md5_hash);
  fclose(f);

  start = strrchr(story_file,'/');
  if (start == NULL) {
    start = story_file;
  } else {
    start++;     // Skip the "/".
  }

  if (strcmp(md5_hash, "A61400439AA76F8FABA3B8F01EDD4A72") == 0) {
    ROM_IDX = ACORNCOURT_;
  } else if (strcmp(md5_hash, "A42545BD17330AE5E6FED02270CCFB4A") == 0) {
    ROM_IDX = ADVENTURELAND_;
  } else if (strcmp(md5_hash, "EE2242E155FD8910921B0F8E04019A3A") == 0) {
    ROM_IDX = ADVENT_;
  } else if (strcmp(md5_hash, "064272BE87DE7106192B6FB743C4DFC4") == 0) {
    ROM_IDX = AFFLICTED_;
  } else if (strcmp(md5_hash, "C043DF8624E0E1E9FDA92F1A74B6E402") == 0) {
    ROM_IDX = ANCHOR_;
  } else if (strcmp(md5_hash, "9BA48C72D96AB3E7956A8570B12D34D6") == 0) {
    ROM_IDX = AWAKEN_;
  } else if (strcmp(md5_hash, "F2CB8F94A7E8DF3B850A758DA26FA387") == 0) {
    ROM_IDX = BALANCES_;
  } else if (strcmp(md5_hash, "5D54E326815B0ED3AFF8EFB8FF02EF2F") == 0) {
    ROM_IDX = BALLYHOO_;
  } else if (strcmp(md5_hash, "F06A42A29A5A4E6AA70958C9AE4C37CD") == 0) {
    ROM_IDX = CURSES_;
  } else if (strcmp(md5_hash, "216EEEBA1C8017A77343DC8482F6F185") == 0) {
    ROM_IDX = CUTTHROAT_;
  } else if (strcmp(md5_hash, "5E56A6E5CDEECDED434A8FD8012FC2C6") == 0) {
    ROM_IDX = DEEPHOME_;
  } else if (strcmp(md5_hash, "822655C9BE83E292E06D3D3B1D6A9734") == 0) {
    ROM_IDX = DETECTIVE_;
  } else if (strcmp(md5_hash, "96D314997E5D3A5A793C83845977D44D") == 0) {
    ROM_IDX = DRAGON_;
  } else if (strcmp(md5_hash, "AD3CDEA88D81033FE29167688BD98C31") == 0) {
    ROM_IDX = ENCHANTER_;
  } else if (strcmp(md5_hash, "4C48BA2C5523D78C5F7F9B7809D16B1D") == 0) {
    ROM_IDX = ENTER_;
  } else if (strcmp(md5_hash, "F275DDF32CE8A9E744D53C3B99C5A658") == 0) {
    ROM_IDX = GOLD_;
  } else if (strcmp(md5_hash, "6666389F60E0C8E4CEB08242A263BB52") == 0) {
    ROM_IDX = HHGG_;
  } else if (strcmp(md5_hash, "1EA91A064941A3F612B20833F0A47DF7") == 0) {
    ROM_IDX = HOLLYWOOD_;
  } else if (strcmp(md5_hash, "253B02C8012710577085B9FD3A155CB7") == 0) {
    ROM_IDX = HUNTDARK_;
  } else if (strcmp(md5_hash, "425FA66869309D7ED7F8EF04A492FBB7") == 0) {
    ROM_IDX = INFIDEL_;
  } else if (strcmp(md5_hash, "84D3CE7CCFAFB873736490811A0CC78C") == 0) {
    ROM_IDX = INHUMANE_;
  } else if (strcmp(md5_hash, "1EEF9C0FA009CA4ADF4872CFC5249D45") == 0) {
    ROM_IDX = JEWEL_;
  } else if (strcmp(md5_hash, "EC55791BE814DB3663AD1AEC0D6B7690") == 0) {
    ROM_IDX = KARN_;
  } else if (strcmp(md5_hash, "DAF57133D346442B983BD333FB586CC4") == 0) {
    ROM_IDX = LIBRARY_;
  } else if (strcmp(md5_hash, "31A0C1E360DCE94AA5BECE5240691D17") == 0) {
    ROM_IDX = LOOSE_;
  } else if (strcmp(md5_hash, "AAF0B90FBB31717481C02832BF412070") == 0) {
    ROM_IDX = LOSTPIG_;
  } else if (strcmp(md5_hash, "646A63307F77DCDCD011F330277AE262") == 0) {
    ROM_IDX = LUDICORP_;
  } else if (strcmp(md5_hash, "5F42FF092A2F30471AE98150EF4DA2E1") == 0) {
    ROM_IDX = LURKING_;
  } else if (strcmp(md5_hash, "BF75B9651CFF0E2D04302F19C443588E") == 0) {
    ROM_IDX = MOONLIT_;
  } else if (strcmp(md5_hash, "570179D4F21B2F600862DBFFBB5AFC3E") == 0) {
    ROM_IDX = MURDAC_;
  } else if (strcmp(md5_hash, "72125F159CCCD581786AC16A2828D4E3") == 0) {
    ROM_IDX = NIGHT_;
  } else if (strcmp(md5_hash, "4C5067169B834D247A30BB08D1039896") == 0) {
    ROM_IDX = NINE05_;
  } else if (strcmp(md5_hash, "80EA198BCA425B6D819C74BFA854236E") == 0) {
    ROM_IDX = OMNIQUEST_;
  } else if (strcmp(md5_hash, "D221DAA82708C4E54447F1A884C239EF") == 0) {
    ROM_IDX = PARTYFOUL_;
  } else if (strcmp(md5_hash, "F24C6863468823B744E910CCFE997C6D") == 0) {
    ROM_IDX = PENTARI_;
  } else if (strcmp(md5_hash, "6487DC814B280F5603C53155DE378D27") == 0) {
    ROM_IDX = PLANETFALL_;
  } else if (strcmp(md5_hash, "6AE4FD54B7E55675EC7E54EC4DD26462") == 0) {
    ROM_IDX = PLUNDERED_;
  } else if (strcmp(md5_hash, "BE6D5FA9587A079782B64739E629461F") == 0) {
    ROM_IDX = REVERB_;
  } else if (strcmp(md5_hash, "EE339DBDBB0792F67E20BD71BAFE0EA5") == 0) {
    ROM_IDX = SEASTALKER_;
  } else if (strcmp(md5_hash, "53BF7A60017E06998CC1542CF35F76FA") == 0) {
    ROM_IDX = SHERBET_;
  } else if (strcmp(md5_hash, "35240654D83F9E7073973D338F9657B8") == 0) {
    ROM_IDX = SHERLOCK_;
  } else if (strcmp(md5_hash, "0FF228D12D7CB470DC1A8E9A5151769B") == 0) {
    ROM_IDX = SNACKTIME_;
  } else if (strcmp(md5_hash, "20F1468A058D0A6DE016AE70022E651C") == 0) {
    ROM_IDX = SORCERER_;
  } else if (strcmp(md5_hash, "7A92CE19A39BEDD970D0F1E296981F71") == 0) {
    ROM_IDX = SPELLBRKR_;
  } else if (strcmp(md5_hash, "808039C4E9554BDD15D7793539B3BD97") == 0) {
    ROM_IDX = SPIRIT_;
  } else if (strcmp(md5_hash, "22A0DDAC6BE15540616C10F1007197F3") == 0) {
    ROM_IDX = TEMPLE_;
  } else if (strcmp(md5_hash, "33DCC5085ACB290D1817E07653C13480") == 0) {
    ROM_IDX = THEATRE_;
  } else if (strcmp(md5_hash, "3BF1A444A1FC2057130ECB9806117233") == 0) {
    ROM_IDX = TRINITY_;
  } else if (strcmp(md5_hash, "FC65AD8D4588DA92FD39871F6F7463DB") == 0) {
    ROM_IDX = TRYST_;
  } else if (strcmp(md5_hash, "C632204BE3849D6C5BB6F4EB5ACA3CC0") == 0) {
    ROM_IDX = WEAPON_;
  } else if (strcmp(md5_hash, "87ED53D854F7E57C36106FCA3B9CF5A6") == 0) {
    ROM_IDX = WISHBRINGER_;
  } else if (strcmp(md5_hash, "5B10162A7A134E7B4C381ECEDFB4BC44") == 0) {
    ROM_IDX = YOMOMMA_;
  } else if (strcmp(md5_hash, "631CC926B4251F5A5F646D3A6BDAC8C6") == 0) {
    ROM_IDX = ZENON_;
  } else if (strcmp(md5_hash, "B732A93A6244DDD92A9B9A3E3A46C687") == 0) {
    ROM_IDX = ZORK1_;
  } else if (strcmp(md5_hash, "5BCD91EE055E9BD42812617571BE227B") == 0) {
    ROM_IDX = ZORK2_;
  } else if (strcmp(md5_hash, "FFDA9EE2D428FA2FA8E75A1914FF6959") == 0) {
    ROM_IDX = ZORK3_;
  } else if (strcmp(md5_hash, "D8E1578470CBC676E013E03D72C93141") == 0) {
    ROM_IDX = ZTUU_;
  } else if (strncmp(start, "tw-", 3) == 0) {
    ROM_IDX = TEXTWORLD_;
  } else {
    ROM_IDX = DEFAULT_;
  }
}

void shutdown() {
  reset_memory();
  dumb_free();
  free_setup();

  free(prev_objs_state); prev_objs_state = NULL;
  free(curr_objs_state); curr_objs_state = NULL;
  free(prev_special_ram); prev_special_ram = NULL;
  free(curr_special_ram); curr_special_ram = NULL;
}

// Save the state of the game into a string buffer
int save_str(unsigned char *s) {
  quetzal_success = 0;
  use_squetzal = 1;
  save_buff = s;
  dumb_set_next_action("save\n");
  zstep();
  run_free();
  if (!quetzal_success) {
      printf("Error During Save: %s\n", dumb_get_screen());
  }
  dumb_clear_screen();
  save_buff = NULL;
  return quetzal_success;
}

// Restore a saved game from a string buffer
int restore_str(unsigned char *s) {
  quetzal_success = 0;
  use_squetzal = 1;
  save_buff = s;
  dumb_set_next_action("restore\n");
  zstep();
  run_free();
  dumb_clear_screen();
  save_buff = NULL;
  return quetzal_success;
}

// Save the state of the game into a file
int save(char *filename) {
  quetzal_success = 0;
  use_squetzal = 0;
  strcpy(f_setup.save_name, filename);
  dumb_set_next_action("save\n");
  zstep();
  run_free();
  dumb_clear_screen();
  return quetzal_success;
}

// Restore a saved file
int restore(char *filename) {
  quetzal_success = 0;
  use_squetzal = 0;
  strcpy(f_setup.save_name, filename);
  dumb_set_next_action("restore\n");
  zstep();
  run_free();
  dumb_clear_screen();
  return quetzal_success;
}

int getRAMSize() {
  return h_dynamic_size;
}

void getRAM(unsigned char *ram) {
  memcpy(ram, zmp, h_dynamic_size);
}

void setRAM(unsigned char *ram) {
  memcpy(zmp, ram, h_dynamic_size);
}

int getPC() {
  return pcp - zmp;
}

void setPC(int v) {
  pcp = zmp + v;
}

int getSP() {
  return sp - stack;
}

void setSP(int v) {
  sp = stack + v;
}

int getFP() {
  return fp - stack;
}

void setFP(int v) {
  fp = stack + v;
}

int getRetPC() {
  return *(fp+2) | (*(fp+2+1) << 9);
}

int get_opcode() {
  return next_opcode;
}

int set_opcode(int opcode) {
  next_opcode = opcode;
}

int getFrameCount() {
  return frame_count;
}

void setFrameCount(int count) {
  frame_count = count;
}

int getStackSize() {
  return STACK_SIZE*sizeof(zword);
}

void getStack(unsigned char *s) {
  memcpy(s, stack, STACK_SIZE*sizeof(zword));
}

void setStack(unsigned char *s) {
  memcpy(stack, s, STACK_SIZE*sizeof(zword));
}

void getZArgs(unsigned char *s) {
  memcpy(s, zargs, 8*sizeof(zword));
}

void setZArgs(unsigned char *s) {
  memcpy(zargs, s, 8*sizeof(zword));
}

//==========================//
//   Function pointers      //
//==========================//

char** (*ram_addr_fns[]) (int* num_actions) = {
  default_ram_addrs,
  acorn_ram_addrs,
  adventureland_ram_addrs,
  advent_ram_addrs,
  afflicted_ram_addrs,
  anchor_ram_addrs,
  awaken_ram_addrs,
  balances_ram_addrs,
  ballyhoo_ram_addrs,
  curses_ram_addrs,
  cutthroat_ram_addrs,
  deephome_ram_addrs,
  detective_ram_addrs,
  dragon_ram_addrs,
  enchanter_ram_addrs,
  enter_ram_addrs,
  gold_ram_addrs,
  hhgg_ram_addrs,
  hollywood_ram_addrs,
  huntdark_ram_addrs,
  infidel_ram_addrs,
  inhumane_ram_addrs,
  jewel_ram_addrs,
  karn_ram_addrs,
  library_ram_addrs,
  loose_ram_addrs,
  lostpig_ram_addrs,
  ludicorp_ram_addrs,
  lurking_ram_addrs,
  moonlit_ram_addrs,
  murdac_ram_addrs,
  night_ram_addrs,
  nine05_ram_addrs,
  omniquest_ram_addrs,
  partyfoul_ram_addrs,
  pentari_ram_addrs,
  planetfall_ram_addrs,
  plundered_ram_addrs,
  reverb_ram_addrs,
  seastalker_ram_addrs,
  sherbet_ram_addrs,
  sherlock_ram_addrs,
  snacktime_ram_addrs,
  sorcerer_ram_addrs,
  spellbrkr_ram_addrs,
  spirit_ram_addrs,
  temple_ram_addrs,
  theatre_ram_addrs,
  trinity_ram_addrs,
  tryst_ram_addrs,
  weapon_ram_addrs,
  wishbringer_ram_addrs,
  yomomma_ram_addrs,
  zenon_ram_addrs,
  zork1_ram_addrs,
  zork2_ram_addrs,
  zork3_ram_addrs,
  ztuu_ram_addrs,
  textworld_ram_addrs
};

char** (*intro_action_fns[]) (int* num_actions) = {
  default_intro_actions,
  acorn_intro_actions,
  adventureland_intro_actions,
  advent_intro_actions,
  afflicted_intro_actions,
  anchor_intro_actions,
  awaken_intro_actions,
  balances_intro_actions,
  ballyhoo_intro_actions,
  curses_intro_actions,
  cutthroat_intro_actions,
  deephome_intro_actions,
  detective_intro_actions,
  dragon_intro_actions,
  enchanter_intro_actions,
  enter_intro_actions,
  gold_intro_actions,
  hhgg_intro_actions,
  hollywood_intro_actions,
  huntdark_intro_actions,
  infidel_intro_actions,
  inhumane_intro_actions,
  jewel_intro_actions,
  karn_intro_actions,
  library_intro_actions,
  loose_intro_actions,
  lostpig_intro_actions,
  ludicorp_intro_actions,
  lurking_intro_actions,
  moonlit_intro_actions,
  murdac_intro_actions,
  night_intro_actions,
  nine05_intro_actions,
  omniquest_intro_actions,
  partyfoul_intro_actions,
  pentari_intro_actions,
  planetfall_intro_actions,
  plundered_intro_actions,
  reverb_intro_actions,
  seastalker_intro_actions,
  sherbet_intro_actions,
  sherlock_intro_actions,
  snacktime_intro_actions,
  sorcerer_intro_actions,
  spellbrkr_intro_actions,
  spirit_intro_actions,
  temple_intro_actions,
  theatre_intro_actions,
  trinity_intro_actions,
  tryst_intro_actions,
  weapon_intro_actions,
  wishbringer_intro_actions,
  yomomma_intro_actions,
  zenon_intro_actions,
  zork1_intro_actions,
  zork2_intro_actions,
  zork3_intro_actions,
  ztuu_intro_actions,
  textworld_intro_actions
};

char* (*clean_observation_fns[]) (char* obs) = {
  default_clean_observation,
  acorn_clean_observation,
  adventureland_clean_observation,
  advent_clean_observation,
  afflicted_clean_observation,
  anchor_clean_observation,
  awaken_clean_observation,
  balances_clean_observation,
  ballyhoo_clean_observation,
  curses_clean_observation,
  cutthroat_clean_observation,
  deephome_clean_observation,
  detective_clean_observation,
  dragon_clean_observation,
  enchanter_clean_observation,
  enter_clean_observation,
  gold_clean_observation,
  hhgg_clean_observation,
  hollywood_clean_observation,
  huntdark_clean_observation,
  infidel_clean_observation,
  inhumane_clean_observation,
  jewel_clean_observation,
  karn_clean_observation,
  library_clean_observation,
  loose_clean_observation,
  lostpig_clean_observation,
  ludicorp_clean_observation,
  lurking_clean_observation,
  moonlit_clean_observation,
  murdac_clean_observation,
  night_clean_observation,
  nine05_clean_observation,
  omniquest_clean_observation,
  partyfoul_clean_observation,
  pentari_clean_observation,
  planetfall_clean_observation,
  plundered_clean_observation,
  reverb_clean_observation,
  seastalker_clean_observation,
  sherbet_clean_observation,
  sherlock_clean_observation,
  snacktime_clean_observation,
  sorcerer_clean_observation,
  spellbrkr_clean_observation,
  spirit_clean_observation,
  temple_clean_observation,
  theatre_clean_observation,
  trinity_clean_observation,
  tryst_clean_observation,
  weapon_clean_observation,
  wishbringer_clean_observation,
  yomomma_clean_observation,
  zenon_clean_observation,
  zork1_clean_observation,
  zork2_clean_observation,
  zork3_clean_observation,
  ztuu_clean_observation,
  textworld_clean_observation
};

int (*victory_fns[]) (void) = {
  default_victory,
  acorn_victory,
  adventureland_victory,
  advent_victory,
  afflicted_victory,
  anchor_victory,
  awaken_victory,
  balances_victory,
  ballyhoo_victory,
  curses_victory,
  cutthroat_victory,
  deephome_victory,
  detective_victory,
  dragon_victory,
  enchanter_victory,
  enter_victory,
  gold_victory,
  hhgg_victory,
  hollywood_victory,
  huntdark_victory,
  infidel_victory,
  inhumane_victory,
  jewel_victory,
  karn_victory,
  library_victory,
  loose_victory,
  lostpig_victory,
  ludicorp_victory,
  lurking_victory,
  moonlit_victory,
  murdac_victory,
  night_victory,
  nine05_victory,
  omniquest_victory,
  partyfoul_victory,
  pentari_victory,
  planetfall_victory,
  plundered_victory,
  reverb_victory,
  seastalker_victory,
  sherbet_victory,
  sherlock_victory,
  snacktime_victory,
  sorcerer_victory,
  spellbrkr_victory,
  spirit_victory,
  temple_victory,
  theatre_victory,
  trinity_victory,
  tryst_victory,
  weapon_victory,
  wishbringer_victory,
  yomomma_victory,
  zenon_victory,
  zork1_victory,
  zork2_victory,
  zork3_victory,
  ztuu_victory,
  textworld_victory
};

int (*game_over_fns[]) (void) = {
  default_game_over,
  acorn_game_over,
  adventureland_game_over,
  advent_game_over,
  afflicted_game_over,
  anchor_game_over,
  awaken_game_over,
  balances_game_over,
  ballyhoo_game_over,
  curses_game_over,
  cutthroat_game_over,
  deephome_game_over,
  detective_game_over,
  dragon_game_over,
  enchanter_game_over,
  enter_game_over,
  gold_game_over,
  hhgg_game_over,
  hollywood_game_over,
  huntdark_game_over,
  infidel_game_over,
  inhumane_game_over,
  jewel_game_over,
  karn_game_over,
  library_game_over,
  loose_game_over,
  lostpig_game_over,
  ludicorp_game_over,
  lurking_game_over,
  moonlit_game_over,
  murdac_game_over,
  night_game_over,
  nine05_game_over,
  omniquest_game_over,
  partyfoul_game_over,
  pentari_game_over,
  planetfall_game_over,
  plundered_game_over,
  reverb_game_over,
  seastalker_game_over,
  sherbet_game_over,
  sherlock_game_over,
  snacktime_game_over,
  sorcerer_game_over,
  spellbrkr_game_over,
  spirit_game_over,
  temple_game_over,
  theatre_game_over,
  trinity_game_over,
  tryst_game_over,
  weapon_game_over,
  wishbringer_game_over,
  yomomma_game_over,
  zenon_game_over,
  zork1_game_over,
  zork2_game_over,
  zork3_game_over,
  ztuu_game_over,
  textworld_game_over
};

int (*get_self_object_num_fns[]) (void) = {
  default_get_self_object_num,
  acorn_get_self_object_num,
  adventureland_get_self_object_num,
  advent_get_self_object_num,
  afflicted_get_self_object_num,
  anchor_get_self_object_num,
  awaken_get_self_object_num,
  balances_get_self_object_num,
  ballyhoo_get_self_object_num,
  curses_get_self_object_num,
  cutthroat_get_self_object_num,
  deephome_get_self_object_num,
  detective_get_self_object_num,
  dragon_get_self_object_num,
  enchanter_get_self_object_num,
  enter_get_self_object_num,
  gold_get_self_object_num,
  hhgg_get_self_object_num,
  hollywood_get_self_object_num,
  huntdark_get_self_object_num,
  infidel_get_self_object_num,
  inhumane_get_self_object_num,
  jewel_get_self_object_num,
  karn_get_self_object_num,
  library_get_self_object_num,
  loose_get_self_object_num,
  lostpig_get_self_object_num,
  ludicorp_get_self_object_num,
  lurking_get_self_object_num,
  moonlit_get_self_object_num,
  murdac_get_self_object_num,
  night_get_self_object_num,
  nine05_get_self_object_num,
  omniquest_get_self_object_num,
  partyfoul_get_self_object_num,
  pentari_get_self_object_num,
  planetfall_get_self_object_num,
  plundered_get_self_object_num,
  reverb_get_self_object_num,
  seastalker_get_self_object_num,
  sherbet_get_self_object_num,
  sherlock_get_self_object_num,
  snacktime_get_self_object_num,
  sorcerer_get_self_object_num,
  spellbrkr_get_self_object_num,
  spirit_get_self_object_num,
  temple_get_self_object_num,
  theatre_get_self_object_num,
  trinity_get_self_object_num,
  tryst_get_self_object_num,
  weapon_get_self_object_num,
  wishbringer_get_self_object_num,
  yomomma_get_self_object_num,
  zenon_get_self_object_num,
  zork1_get_self_object_num,
  zork2_get_self_object_num,
  zork3_get_self_object_num,
  ztuu_get_self_object_num,
  textworld_get_self_object_num
};

int (*get_moves_fns[]) (void) = {
  default_get_moves,
  acorn_get_moves,
  adventureland_get_moves,
  advent_get_moves,
  afflicted_get_moves,
  anchor_get_moves,
  awaken_get_moves,
  balances_get_moves,
  ballyhoo_get_moves,
  curses_get_moves,
  cutthroat_get_moves,
  deephome_get_moves,
  detective_get_moves,
  dragon_get_moves,
  enchanter_get_moves,
  enter_get_moves,
  gold_get_moves,
  hhgg_get_moves,
  hollywood_get_moves,
  huntdark_get_moves,
  infidel_get_moves,
  inhumane_get_moves,
  jewel_get_moves,
  karn_get_moves,
  library_get_moves,
  loose_get_moves,
  lostpig_get_moves,
  ludicorp_get_moves,
  lurking_get_moves,
  moonlit_get_moves,
  murdac_get_moves,
  night_get_moves,
  nine05_get_moves,
  omniquest_get_moves,
  partyfoul_get_moves,
  pentari_get_moves,
  planetfall_get_moves,
  plundered_get_moves,
  reverb_get_moves,
  seastalker_get_moves,
  sherbet_get_moves,
  sherlock_get_moves,
  snacktime_get_moves,
  sorcerer_get_moves,
  spellbrkr_get_moves,
  spirit_get_moves,
  temple_get_moves,
  theatre_get_moves,
  trinity_get_moves,
  tryst_get_moves,
  weapon_get_moves,
  wishbringer_get_moves,
  yomomma_get_moves,
  zenon_get_moves,
  zork1_get_moves,
  zork2_get_moves,
  zork3_get_moves,
  ztuu_get_moves,
  textworld_get_moves
};

short (*get_score_fns[]) (void) = {
  default_get_score,
  acorn_get_score,
  adventureland_get_score,
  advent_get_score,
  afflicted_get_score,
  anchor_get_score,
  awaken_get_score,
  balances_get_score,
  ballyhoo_get_score,
  curses_get_score,
  cutthroat_get_score,
  deephome_get_score,
  detective_get_score,
  dragon_get_score,
  enchanter_get_score,
  enter_get_score,
  gold_get_score,
  hhgg_get_score,
  hollywood_get_score,
  huntdark_get_score,
  infidel_get_score,
  inhumane_get_score,
  jewel_get_score,
  karn_get_score,
  library_get_score,
  loose_get_score,
  lostpig_get_score,
  ludicorp_get_score,
  lurking_get_score,
  moonlit_get_score,
  murdac_get_score,
  night_get_score,
  nine05_get_score,
  omniquest_get_score,
  partyfoul_get_score,
  pentari_get_score,
  planetfall_get_score,
  plundered_get_score,
  reverb_get_score,
  seastalker_get_score,
  sherbet_get_score,
  sherlock_get_score,
  snacktime_get_score,
  sorcerer_get_score,
  spellbrkr_get_score,
  spirit_get_score,
  temple_get_score,
  theatre_get_score,
  trinity_get_score,
  tryst_get_score,
  weapon_get_score,
  wishbringer_get_score,
  yomomma_get_score,
  zenon_get_score,
  zork1_get_score,
  zork2_get_score,
  zork3_get_score,
  ztuu_get_score,
  textworld_get_score
};

int (*get_num_world_objs_fns[]) (void) = {
  default_get_num_world_objs,
  acorn_get_num_world_objs,
  adventureland_get_num_world_objs,
  advent_get_num_world_objs,
  afflicted_get_num_world_objs,
  anchor_get_num_world_objs,
  awaken_get_num_world_objs,
  balances_get_num_world_objs,
  ballyhoo_get_num_world_objs,
  curses_get_num_world_objs,
  cutthroat_get_num_world_objs,
  deephome_get_num_world_objs,
  detective_get_num_world_objs,
  dragon_get_num_world_objs,
  enchanter_get_num_world_objs,
  enter_get_num_world_objs,
  gold_get_num_world_objs,
  hhgg_get_num_world_objs,
  hollywood_get_num_world_objs,
  huntdark_get_num_world_objs,
  infidel_get_num_world_objs,
  inhumane_get_num_world_objs,
  jewel_get_num_world_objs,
  karn_get_num_world_objs,
  library_get_num_world_objs,
  loose_get_num_world_objs,
  lostpig_get_num_world_objs,
  ludicorp_get_num_world_objs,
  lurking_get_num_world_objs,
  moonlit_get_num_world_objs,
  murdac_get_num_world_objs,
  night_get_num_world_objs,
  nine05_get_num_world_objs,
  omniquest_get_num_world_objs,
  partyfoul_get_num_world_objs,
  pentari_get_num_world_objs,
  planetfall_get_num_world_objs,
  plundered_get_num_world_objs,
  reverb_get_num_world_objs,
  seastalker_get_num_world_objs,
  sherbet_get_num_world_objs,
  sherlock_get_num_world_objs,
  snacktime_get_num_world_objs,
  sorcerer_get_num_world_objs,
  spellbrkr_get_num_world_objs,
  spirit_get_num_world_objs,
  temple_get_num_world_objs,
  theatre_get_num_world_objs,
  trinity_get_num_world_objs,
  tryst_get_num_world_objs,
  weapon_get_num_world_objs,
  wishbringer_get_num_world_objs,
  yomomma_get_num_world_objs,
  zenon_get_num_world_objs,
  zork1_get_num_world_objs,
  zork2_get_num_world_objs,
  zork3_get_num_world_objs,
  ztuu_get_num_world_objs,
  textworld_get_num_world_objs
};

int (*max_score_fns[]) (void) = {
  default_max_score,
  acorn_max_score,
  adventureland_max_score,
  advent_max_score,
  afflicted_max_score,
  anchor_max_score,
  awaken_max_score,
  balances_max_score,
  ballyhoo_max_score,
  curses_max_score,
  cutthroat_max_score,
  deephome_max_score,
  detective_max_score,
  dragon_max_score,
  enchanter_max_score,
  enter_max_score,
  gold_max_score,
  hhgg_max_score,
  hollywood_max_score,
  huntdark_max_score,
  infidel_max_score,
  inhumane_max_score,
  jewel_max_score,
  karn_max_score,
  library_max_score,
  loose_max_score,
  lostpig_max_score,
  ludicorp_max_score,
  lurking_max_score,
  moonlit_max_score,
  murdac_max_score,
  night_max_score,
  nine05_max_score,
  omniquest_max_score,
  partyfoul_max_score,
  pentari_max_score,
  planetfall_max_score,
  plundered_max_score,
  reverb_max_score,
  seastalker_max_score,
  sherbet_max_score,
  sherlock_max_score,
  snacktime_max_score,
  sorcerer_max_score,
  spellbrkr_max_score,
  spirit_max_score,
  temple_max_score,
  theatre_max_score,
  trinity_max_score,
  tryst_max_score,
  weapon_max_score,
  wishbringer_max_score,
  yomomma_max_score,
  zenon_max_score,
  zork1_max_score,
  zork2_max_score,
  zork3_max_score,
  ztuu_max_score,
  textworld_max_score
};

int (*ignore_moved_obj_fns[]) (zword obj_num, zword dest_num) = {
  default_ignore_moved_obj,
  acorn_ignore_moved_obj,
  adventureland_ignore_moved_obj,
  advent_ignore_moved_obj,
  afflicted_ignore_moved_obj,
  anchor_ignore_moved_obj,
  awaken_ignore_moved_obj,
  balances_ignore_moved_obj,
  ballyhoo_ignore_moved_obj,
  curses_ignore_moved_obj,
  cutthroat_ignore_moved_obj,
  deephome_ignore_moved_obj,
  detective_ignore_moved_obj,
  dragon_ignore_moved_obj,
  enchanter_ignore_moved_obj,
  enter_ignore_moved_obj,
  gold_ignore_moved_obj,
  hhgg_ignore_moved_obj,
  hollywood_ignore_moved_obj,
  huntdark_ignore_moved_obj,
  infidel_ignore_moved_obj,
  inhumane_ignore_moved_obj,
  jewel_ignore_moved_obj,
  karn_ignore_moved_obj,
  library_ignore_moved_obj,
  loose_ignore_moved_obj,
  lostpig_ignore_moved_obj,
  ludicorp_ignore_moved_obj,
  lurking_ignore_moved_obj,
  moonlit_ignore_moved_obj,
  murdac_ignore_moved_obj,
  night_ignore_moved_obj,
  nine05_ignore_moved_obj,
  omniquest_ignore_moved_obj,
  partyfoul_ignore_moved_obj,
  pentari_ignore_moved_obj,
  planetfall_ignore_moved_obj,
  plundered_ignore_moved_obj,
  reverb_ignore_moved_obj,
  seastalker_ignore_moved_obj,
  sherbet_ignore_moved_obj,
  sherlock_ignore_moved_obj,
  snacktime_ignore_moved_obj,
  sorcerer_ignore_moved_obj,
  spellbrkr_ignore_moved_obj,
  spirit_ignore_moved_obj,
  temple_ignore_moved_obj,
  theatre_ignore_moved_obj,
  trinity_ignore_moved_obj,
  tryst_ignore_moved_obj,
  weapon_ignore_moved_obj,
  wishbringer_ignore_moved_obj,
  yomomma_ignore_moved_obj,
  zenon_ignore_moved_obj,
  zork1_ignore_moved_obj,
  zork2_ignore_moved_obj,
  zork3_ignore_moved_obj,
  ztuu_ignore_moved_obj,
  textworld_ignore_moved_obj
};

int (*ignore_attr_diff_fns[]) (zword obj_num, zword attr_idx) = {
  default_ignore_attr_diff,
  acorn_ignore_attr_diff,
  adventureland_ignore_attr_diff,
  advent_ignore_attr_diff,
  afflicted_ignore_attr_diff,
  anchor_ignore_attr_diff,
  awaken_ignore_attr_diff,
  balances_ignore_attr_diff,
  ballyhoo_ignore_attr_diff,
  curses_ignore_attr_diff,
  cutthroat_ignore_attr_diff,
  deephome_ignore_attr_diff,
  detective_ignore_attr_diff,
  dragon_ignore_attr_diff,
  enchanter_ignore_attr_diff,
  enter_ignore_attr_diff,
  gold_ignore_attr_diff,
  hhgg_ignore_attr_diff,
  hollywood_ignore_attr_diff,
  huntdark_ignore_attr_diff,
  infidel_ignore_attr_diff,
  inhumane_ignore_attr_diff,
  jewel_ignore_attr_diff,
  karn_ignore_attr_diff,
  library_ignore_attr_diff,
  loose_ignore_attr_diff,
  lostpig_ignore_attr_diff,
  ludicorp_ignore_attr_diff,
  lurking_ignore_attr_diff,
  moonlit_ignore_attr_diff,
  murdac_ignore_attr_diff,
  night_ignore_attr_diff,
  nine05_ignore_attr_diff,
  omniquest_ignore_attr_diff,
  partyfoul_ignore_attr_diff,
  pentari_ignore_attr_diff,
  planetfall_ignore_attr_diff,
  plundered_ignore_attr_diff,
  reverb_ignore_attr_diff,
  seastalker_ignore_attr_diff,
  sherbet_ignore_attr_diff,
  sherlock_ignore_attr_diff,
  snacktime_ignore_attr_diff,
  sorcerer_ignore_attr_diff,
  spellbrkr_ignore_attr_diff,
  spirit_ignore_attr_diff,
  temple_ignore_attr_diff,
  theatre_ignore_attr_diff,
  trinity_ignore_attr_diff,
  tryst_ignore_attr_diff,
  weapon_ignore_attr_diff,
  wishbringer_ignore_attr_diff,
  yomomma_ignore_attr_diff,
  zenon_ignore_attr_diff,
  zork1_ignore_attr_diff,
  zork2_ignore_attr_diff,
  zork3_ignore_attr_diff,
  ztuu_ignore_attr_diff,
  textworld_ignore_attr_diff
};

int (*ignore_attr_clr_fns[]) (zword obj_num, zword attr_idx) = {
  default_ignore_attr_clr,
  acorn_ignore_attr_clr,
  adventureland_ignore_attr_clr,
  advent_ignore_attr_clr,
  afflicted_ignore_attr_clr,
  anchor_ignore_attr_clr,
  awaken_ignore_attr_clr,
  balances_ignore_attr_clr,
  ballyhoo_ignore_attr_clr,
  curses_ignore_attr_clr,
  cutthroat_ignore_attr_clr,
  deephome_ignore_attr_clr,
  detective_ignore_attr_clr,
  dragon_ignore_attr_clr,
  enchanter_ignore_attr_clr,
  enter_ignore_attr_clr,
  gold_ignore_attr_clr,
  hhgg_ignore_attr_clr,
  hollywood_ignore_attr_clr,
  huntdark_ignore_attr_clr,
  infidel_ignore_attr_clr,
  inhumane_ignore_attr_clr,
  jewel_ignore_attr_clr,
  karn_ignore_attr_clr,
  library_ignore_attr_clr,
  loose_ignore_attr_clr,
  lostpig_ignore_attr_clr,
  ludicorp_ignore_attr_clr,
  lurking_ignore_attr_clr,
  moonlit_ignore_attr_clr,
  murdac_ignore_attr_clr,
  night_ignore_attr_clr,
  nine05_ignore_attr_clr,
  omniquest_ignore_attr_clr,
  partyfoul_ignore_attr_clr,
  pentari_ignore_attr_clr,
  planetfall_ignore_attr_clr,
  plundered_ignore_attr_clr,
  reverb_ignore_attr_clr,
  seastalker_ignore_attr_clr,
  sherbet_ignore_attr_clr,
  sherlock_ignore_attr_clr,
  snacktime_ignore_attr_clr,
  sorcerer_ignore_attr_clr,
  spellbrkr_ignore_attr_clr,
  spirit_ignore_attr_clr,
  temple_ignore_attr_clr,
  theatre_ignore_attr_clr,
  trinity_ignore_attr_clr,
  tryst_ignore_attr_clr,
  weapon_ignore_attr_clr,
  wishbringer_ignore_attr_clr,
  yomomma_ignore_attr_clr,
  zenon_ignore_attr_clr,
  zork1_ignore_attr_clr,
  zork2_ignore_attr_clr,
  zork3_ignore_attr_clr,
  ztuu_ignore_attr_clr,
  textworld_ignore_attr_clr
};

void (*clean_world_objs_fns[]) (zobject* objs) = {
  default_clean_world_objs,
  acorn_clean_world_objs,
  adventureland_clean_world_objs,
  advent_clean_world_objs,
  afflicted_clean_world_objs,
  anchor_clean_world_objs,
  awaken_clean_world_objs,
  balances_clean_world_objs,
  ballyhoo_clean_world_objs,
  curses_clean_world_objs,
  cutthroat_clean_world_objs,
  deephome_clean_world_objs,
  detective_clean_world_objs,
  dragon_clean_world_objs,
  enchanter_clean_world_objs,
  enter_clean_world_objs,
  gold_clean_world_objs,
  hhgg_clean_world_objs,
  hollywood_clean_world_objs,
  huntdark_clean_world_objs,
  infidel_clean_world_objs,
  inhumane_clean_world_objs,
  jewel_clean_world_objs,
  karn_clean_world_objs,
  library_clean_world_objs,
  loose_clean_world_objs,
  lostpig_clean_world_objs,
  ludicorp_clean_world_objs,
  lurking_clean_world_objs,
  moonlit_clean_world_objs,
  murdac_clean_world_objs,
  night_clean_world_objs,
  nine05_clean_world_objs,
  omniquest_clean_world_objs,
  partyfoul_clean_world_objs,
  pentari_clean_world_objs,
  planetfall_clean_world_objs,
  plundered_clean_world_objs,
  reverb_clean_world_objs,
  seastalker_clean_world_objs,
  sherbet_clean_world_objs,
  sherlock_clean_world_objs,
  snacktime_clean_world_objs,
  sorcerer_clean_world_objs,
  spellbrkr_clean_world_objs,
  spirit_clean_world_objs,
  temple_clean_world_objs,
  theatre_clean_world_objs,
  trinity_clean_world_objs,
  tryst_clean_world_objs,
  weapon_clean_world_objs,
  wishbringer_clean_world_objs,
  yomomma_clean_world_objs,
  zenon_clean_world_objs,
  zork1_clean_world_objs,
  zork2_clean_world_objs,
  zork3_clean_world_objs,
  ztuu_clean_world_objs,
  textworld_clean_world_objs
};


//================================//
// ZObject Manipulation Functions //
//================================//

void clear_attr(zobject* obj, unsigned char attr_id) {
  // attr[0]  attr[1]  attr[2]  attr[3]
  // 11111111 11111011 11111111 11111111
  // ^        ^    ^   ^        ^
  // 0        8   13  16       24
  //
  // bit = 8 - (13 % 8) - 1 = 2
  // mask = ~(1 << 2) = 0b11111011
  char bit = 8 - (attr_id % 8) - 1;
  char mask = ~(1 << bit);
  obj->attr[attr_id / 8] &= mask;
}

void clear_prop(zobject* obj, unsigned char prop_id) {
  for (int i=0; i < JERICHO_NB_PROPERTIES; ++i) {
    if (obj->prop_ids[i] == prop_id) {
      memset(&obj->prop_data[i * JERICHO_PROPERTY_LENGTH], 0, obj->prop_lengths[i] * sizeof(zbyte));
      break;
    }
  }
}

//==========================//
// Function Instantiations  //
//==========================//

zword* get_ram_addrs(int* num_addrs) {
  return (*ram_addr_fns[ROM_IDX])(num_addrs);
}

char** get_intro_actions(int* num_actions) {
  return (*intro_action_fns[ROM_IDX])(num_actions);
}

char* clean_observation(char* obs) {
  char* out = (*clean_observation_fns[ROM_IDX])(obs);
  out = trim_whitespaces(out);
  // printf("-<obs>-\n%s\n-</obs>-", out);  // For debugging.
  return out;
}

short get_score() {
  return (*get_score_fns[ROM_IDX])();
}

int get_max_score() {
  return (*max_score_fns[ROM_IDX])();
}

int get_moves() {
  return (*get_moves_fns[ROM_IDX])();
}

int get_self_object_num() {
  return (*get_self_object_num_fns[ROM_IDX])();
}

int get_num_world_objs() {
  return (*get_num_world_objs_fns[ROM_IDX])();
}

int game_over() {
  return emulator_halted > 0 || (*game_over_fns[ROM_IDX])();
}

int victory() {
  return (*victory_fns[ROM_IDX])();
}

int halted() {
  return emulator_halted;
}

void clean_world_objs(zobject* objs) {
  return (*clean_world_objs_fns[ROM_IDX])(objs);
}

int is_supported(char *story_file) {
  load_rom_bindings(story_file);
  return ROM_IDX != DEFAULT_;
}

// Takes game-specific introduction actions
void take_intro_actions() {
  int num_actions = 0;
  char **intro_actions = NULL;
  intro_actions = get_intro_actions(&num_actions);
  if (num_actions <= 0 || intro_actions == NULL)
    return;

  char* text;
  for (int i=0; i<num_actions; ++i) {
    strcat(world, dumb_get_lower_screen());
    dumb_clear_lower_screen();

    dumb_set_next_action(intro_actions[i]);
    zstep();
    run_free();
  }
}

// Returns the number of special ram addresses
int get_special_ram_size() {
  int num_special_addrs;
  get_ram_addrs(&num_special_addrs);
  return num_special_addrs;
}

// Returns the current values of the special ram addresses
void get_special_ram(zbyte *ram) {
  int num_special_addrs;
  zword* special_ram_addrs = get_ram_addrs(&num_special_addrs);
  for (int i=0; i<num_special_addrs; ++i) {
    ram[i] = zmp[special_ram_addrs[i]];
  }
}

// Returns the special ram addresses.
void get_special_ram_addrs(zword *ram_addrs) {
  int num_special_addrs;
  zword* special_ram_addrs = get_ram_addrs(&num_special_addrs);
  for (int i=0; i<num_special_addrs; ++i) {
    ram_addrs[i] = special_ram_addrs[i];
  }
}

// Create memory used to hold the special ram values.
void init_special_ram_tracker() {
  if (prev_special_ram) { free(prev_special_ram); }
  if (curr_special_ram) { free(curr_special_ram); }
  prev_special_ram = calloc(get_special_ram_size(), sizeof(zbyte));
  curr_special_ram = calloc(get_special_ram_size(), sizeof(zbyte));
}

// Create memory used to hold the objects' state.
void init_objects_tracker() {
  free(prev_objs_state); prev_objs_state = NULL;
  free(curr_objs_state); curr_objs_state = NULL;
  prev_objs_state = calloc(get_num_world_objs() + 1, sizeof(zobject));
  curr_objs_state = calloc(get_num_world_objs() + 1, sizeof(zobject));
}

// Updates the special ram values to reflect the current memory
void update_special_ram_tracker() {
  get_special_ram(curr_special_ram);
}

// Updates the objects list, used for tracking state changes, to reflect the current memory
void update_objs_tracker() {
  get_world_objects(curr_objs_state, TRUE);

  // For a more robust state hash, do not include siblings and children
  // since their ordering in memory may change.
  for (int i=1; i<=get_num_world_objs(); ++i) {
    curr_objs_state[i].sibling = 0;
    curr_objs_state[i].child = 0;
  }
}

void get_prev_objs_state(zobject *objs_state) {
  memcpy(objs_state, prev_objs_state, (get_num_world_objs() + 1) * sizeof(zobject));
}

void set_prev_objs_state(zobject *objs_state) {
  memcpy(prev_objs_state, objs_state, (get_num_world_objs() + 1) * sizeof(zobject));
}

void get_prev_special_ram(zbyte *ram) {
  memcpy(ram, prev_special_ram, get_special_ram_size() * sizeof(zbyte));
}

void set_prev_special_ram(zbyte *ram) {
  memcpy(prev_special_ram, ram, get_special_ram_size() * sizeof(zbyte));
}


char* setup(char *story_file, int seed, void *rom, size_t rom_size) {
  char* text;
  emulator_halted = 0;
  os_init_setup();
  desired_seed = seed;
  set_random_seed(desired_seed);
  if (rom) {
    load_story_rom(story_file, rom, rom_size);
  }
  else {
    load_story(story_file);
  }
  init_buffer();
  init_err();
  init_memory();
  init_process();
  init_sound();
  os_init_screen();
  init_undo();
  z_restart();
  next_opcode = get_next_opcode();
  dumb_set_next_action("\n");
  zstep();
  run_free();
  load_rom_bindings(story_file);

  world[0] = '\0';  // Clear lower screen buffer.
  take_intro_actions();
  init_special_ram_tracker();
  init_objects_tracker();

  // Extra procedures for TextWorld
  if (ROM_IDX == TEXTWORLD_) {
    dumb_clear_screen();
    dumb_set_next_action("tw-print max_score\n");
    zstep();
    run_free();
    char* text = dumb_get_screen();
    tw_max_score = strtol(text, NULL, 10);
    dumb_clear_screen();
    dumb_set_next_action("tw-print EndOfObject id\n");
    zstep();
    run_free();
    text = dumb_get_screen();
    tw_num_world_objs = strtol(text, NULL, 10);
    dumb_clear_screen();
    dumb_set_next_action("tw-print player id\n");
    zstep();
    run_free();
    text = dumb_get_screen();
    tw_player_obj_num = strtol(text, NULL, 10);
    dumb_clear_screen();
    z_restart();
    next_opcode = get_next_opcode();
    zstep();
    run_free();
  }

  // Concatenate upper and lower screens.
  strcat(world, dumb_get_lower_screen());
  strcat(world, dumb_get_upper_screen());
  strcpy(world, clean_observation(world));

  dumb_clear_lower_screen();
  dumb_clear_upper_screen();

  return world;
}

char* jericho_step(char *next_action) {
  if (emulator_halted == 1)
    return halted_message;

  if (emulator_halted == 2)
    return "Emulator has stopped.";

  // Swap prev_objs_state and curr_objs_state.
  zobject* tmp_objs_state;
  tmp_objs_state = prev_objs_state;
  prev_objs_state = curr_objs_state;
  curr_objs_state = tmp_objs_state;

  // Swap prev_special_ram and curr_special_ram.
  zword* tmp_special_ram;
  tmp_special_ram = prev_special_ram;
  prev_special_ram = curr_special_ram;
  curr_special_ram = tmp_special_ram;

  // Clear the object, attr, and ram diffs
  last_ret_pc = getRetPC();

  dumb_set_next_action(next_action);

  zstep();
  run_free();

  // Check for changes to special ram
  update_objs_tracker();
  update_special_ram_tracker();

  objects_state_changed = memcmp(prev_objs_state, curr_objs_state, (get_num_world_objs() + 1) * sizeof(zobject)) != 0;
  special_ram_changed = memcmp(prev_special_ram, curr_special_ram, get_special_ram_size() * sizeof(zbyte)) != 0;

  // Retrieve and concatenate upper and lower screens.
  strcpy(world, dumb_get_lower_screen());
  strcat(world, dumb_get_upper_screen());
  strcpy(world, clean_observation(world));
  dumb_clear_lower_screen();
  dumb_clear_upper_screen();

  return world;
}

char* get_narrative_text() {
  return world;
}

void set_narrative_text(char* text) {
  strcpy(world, text);
}

bool get_objects_state_changed() {
  return objects_state_changed;
}

void set_objects_state_changed(bool value) {
  objects_state_changed = value;
}

bool get_special_ram_changed() {
  return special_ram_changed;
}

void set_special_ram_changed(bool value) {
  special_ram_changed = value;
}

char* get_current_state() {
  return world;
}

// Returns 1 if the last action changed the state of the world.
int world_changed() {
  if (game_over() > 0 || victory() > 0) {
    return 1;
  }

  return objects_state_changed || special_ram_changed || last_ret_pc != getRetPC();
}


void get_object(zobject *obj, zword obj_num) {
  zbyte prop_value;
  zbyte mask;

  if (obj_num < 1 || obj_num > get_num_world_objs()) {
    return;
  }

  zword obj_name_addr = object_name(obj_num);
  zbyte length;
  LOW_BYTE(obj_name_addr, length);

  (*obj).num = obj_num;

  if (length > 0 && length <= 64) {
    get_text(0, obj_name_addr+1, &(*obj).name);
  }
  else if (length > 64) {
    // Object's short name is limited to 765 Z-characters.
    // https://inform-fiction.org/zmachine/standards/z1point1/sect12.html#four.
    char* buf = calloc(length, 1);
    get_text(0, obj_name_addr+1, buf);
    memcpy(&(*obj).name, buf, 64);  // Crop the name to the first 64 characters.
    free(buf);
  }

  (*obj).parent = get_parent(obj_num);
  (*obj).sibling = get_sibling(obj_num);
  (*obj).child = get_child(obj_num);

  // Get the attributes of the object
  zword obj_addr = object_address(obj_num);
  for (int i=0; i<4; ++i) {
    LOW_BYTE(obj_addr + i, (*obj).attr[i]);
  }

  // Get the properties of the object
  zbyte value;
  zbyte prop_id;
  zword wprop_val;
  zbyte bprop_val;
  zword prop_data_addr;

  /* Property id is in bottom five (six) bits */
  mask = (h_version <= V3) ? 0x1f : 0x3f;
  zword prop_addr = first_property (obj_num);

  /* Scan down the property list */
  int i;
  for (i=0; i < JERICHO_NB_PROPERTIES; ++i) {
    LOW_BYTE (prop_addr, value)
    prop_id = value & mask;
    if (prop_id <= 0)
        break;

    (*obj).prop_ids[i] = prop_id;

    /* Load property (byte or word sized) */
    prop_data_addr = prop_addr + 1;
    prop_addr = next_property (prop_addr);
    zbyte prop_len = prop_addr - prop_data_addr - 1;

    (*obj).prop_lengths[i] = prop_len;

    // Zero-initialized the property data.
    for (int j=0; j < JERICHO_PROPERTY_LENGTH; ++j) {
      (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + j] = 0;
    }

    if (prop_len <= 2) {
      if ((h_version <= V3 && !(value & 0xe0)) || (h_version >= V4 && !(value & 0xc0))) {
          LOW_BYTE (prop_data_addr, bprop_val)
          wprop_val = bprop_val;
          (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + 0] = bprop_val;
      } else {
        LOW_WORD (prop_data_addr, wprop_val)
        (*obj).prop_lengths[i] += 1;  // zword is two zbytes.
        (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + 0] = zmp[prop_data_addr];
        (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + 1] = zmp[prop_data_addr+1];
      }

    } else {
      prop_data_addr++;  // Property data starts on the next zbyte.
      for (int j=0; j < prop_len; ++j) {
        (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + j] = zmp[prop_data_addr + j];
      }
    }
  }

  // Zero-initialize the remaining properties.
  for (; i<JERICHO_NB_PROPERTIES; ++i) {
    (*obj).prop_ids[i] = 0;
    (*obj).prop_lengths[i] = 0;

    for (int j=0; j < JERICHO_PROPERTY_LENGTH; ++j) {
      (*obj).prop_data[(i*JERICHO_PROPERTY_LENGTH) + j] = 0;
    }
  }
}

void get_world_objects(zobject *objs, int clean) {
  for (int i=1; i<=get_num_world_objs(); ++i) {
    get_object(&objs[i], (zword) i);
  }
  if (clean > 0) {
    clean_world_objs(objs);
  }
}


#define BYTE_TO_BINARY_PATTERN "%c%c%c%c%c%c%c%c "
#define BYTE_TO_BINARY(byte)  \
  (byte & 0x80 ? '1' : '0'), \
  (byte & 0x40 ? '1' : '0'), \
  (byte & 0x20 ? '1' : '0'), \
  (byte & 0x10 ? '1' : '0'), \
  (byte & 0x08 ? '1' : '0'), \
  (byte & 0x04 ? '1' : '0'), \
  (byte & 0x02 ? '1' : '0'), \
  (byte & 0x01 ? '1' : '0')

// Print all information related to a given object.
// Useful for debugging.
void print_zobject(zobject* obj) {
  //
  printf("Obj%d: %s Parent%d Sibling%d Child%d", obj->num, obj->name, obj->parent, obj->sibling, obj->child);

  printf(" Attributes [");
  for (int i=0; i != 4; ++i) {
    printf(BYTE_TO_BINARY_PATTERN, BYTE_TO_BINARY(obj->attr[i]));
  }
  printf("] Properties [");
  for (int i=0; i != 64; ++i) {
    if (obj->prop_ids[i] != 0) {
      printf("%d ", obj->prop_ids[i]);
    }
  }

  printf("]\n");
  }

void get_world_state_hash(char* md5_hash) {
  int n_objs = get_num_world_objs() + 1; // Add extra spot for zero'th object
  size_t objs_size = n_objs * sizeof(zobject);
  size_t ram_size = get_special_ram_size() * sizeof(unsigned char);

  int retPC = getRetPC();

  size_t state_size = objs_size + ram_size + sizeof(int);
  char* state = malloc(state_size);

  memcpy(state, curr_objs_state, objs_size);
  memcpy(&state[objs_size], curr_special_ram, ram_size);
  memcpy(&state[objs_size+ram_size], &retPC, sizeof(int));

  FILE* fp = fmemopen(state, state_size, "rb");
  sum(fp, md5_hash);
  fclose(fp);

  // printf("md5 (objs): %s\n", md5_hash);  // For debugging.

  free(state);
}

// Teleports an object (and all children) to the desired destination
void teleport_obj(zword obj, zword dest) {
  insert_obj(obj, dest);
}

// Teleports an object (and all siblings + children + children of
// siblings) to the last child of desired destination
void teleport_tree(zword obj, zword dest) {
  insert_tree(obj, dest);
}

// Given a list of action candidates, find the ones that lead to valid world changes.
// 'candidate_actions' contains a string with all the candidate actions, seperated by ';'
// 'valid_actions' will be written with each of the identified valid actions seperated by ';'
// 'hashes' will be written with the resulting state hashe for each valid action indicating
// which of the valid actions are equivalent to each other in terms of their state hashes.
// Returns the number of valid actions found.
int filter_candidate_actions(char *candidate_actions, char *valid_actions, char *hashes) {

  char *act = NULL;
  char *act_newline = NULL;
  char *text;
  int valid_cnt = 0;
  int v_idx = 0;

  // Variables used to store & reset game state
  unsigned char ram_cpy[h_dynamic_size];
  unsigned char stack_cpy[STACK_SIZE*sizeof(zword)];

  // Save the game state
  getRAM(ram_cpy);
  getStack(stack_cpy);
  int pc_cpy = getPC();
  int sp_cpy = getSP();
  int fp_cpy = getFP();
  int next_opcode_cpy = get_opcode();
  int frame_count_cpy = getFrameCount();
  long rngA_cpy = getRngA();
  int rngInterval_cpy = getRngInterval();
  int rngCounter_cpy = getRngCounter();
  bool objects_state_changed_cpy = get_objects_state_changed();
  bool special_ram_changed_cpy = get_special_ram_changed();

  short orig_score = get_score();

  act = strtok(candidate_actions, ";");
  while (act != NULL)
  {
    // Add a newline and termination to act
    act_newline = malloc(strlen(act) + 2);
    strcpy(act_newline, act);
    strcat(act_newline, "\n");
    text = jericho_step(act_newline);

    if (emulator_halted > 0) {
      printf("Emulator halted on action: %s\n", act);
      return valid_cnt;
    }

    if (get_score() != orig_score || game_over() > 0 || victory() > 0 || world_changed() > 0) {
      // Ignore actions with side-effect of taking items
      if (strstr(text, "(Taken)") == NULL) {
        // Copy the valid action into the output array
        strcpy(&valid_actions[v_idx], act);
        v_idx += strlen(act);
        valid_actions[v_idx++] = ';';

        // Write the world diff resulting from the last action.
        get_world_state_hash(&hashes[32*valid_cnt]);
        valid_cnt++;
      }
    }

    // Restore the game state
    setRng(rngA_cpy, rngInterval_cpy, rngCounter_cpy);
    setRAM(ram_cpy);
    setStack(stack_cpy);
    setPC(pc_cpy);
    setSP(sp_cpy);
    setFP(fp_cpy);
    set_opcode(next_opcode_cpy);
    setFrameCount(frame_count_cpy);
    update_objs_tracker();
    update_special_ram_tracker();
    set_objects_state_changed(objects_state_changed_cpy);
    set_special_ram_changed(special_ram_changed_cpy);

    act = strtok(NULL, ";");
    free(act_newline);
  }

  return valid_cnt;
}
