/*
 * dumb_output.c - Dumb interface, output functions
 *
 * This file is part of Frotz.
 *
 * Frotz is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Frotz is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
 * Or visit http://www.fsf.org/
 */

#include "dumb_frotz.h"

extern f_setup_t f_setup;

static bool show_line_numbers = FALSE;
static bool show_line_types = -1;
static bool show_pictures = TRUE;
static bool visual_bell = FALSE;
static bool plain_ascii = FALSE;

static char latin1_to_ascii[] =
  "    !   c   L   >o< Y   |   S   ''  C   a   <<  not -   R   _   "
  "^0  +/- ^2  ^3  '   my  P   .   ,   ^1  o   >>  1/4 1/2 3/4 ?   "
  "A   A   A   A   Ae  A   AE  C   E   E   E   E   I   I   I   I   "
  "Th  N   O   O   O   O   Oe  *   O   U   U   U   Ue  Y   Th  ss  "
  "a   a   a   a   ae  a   ae  c   e   e   e   e   i   i   i   i   "
  "th  n   o   o   o   o   oe  :   o   u   u   u   ue  y   th  y   "
;

/* h_screen_rows * h_screen_cols */
static int screen_cells;

/* The in-memory state of the screen.  */
/* Each cell contains a style in the upper byte and a char in the lower. */
typedef unsigned short cell;
static cell *screen_data;

static cell make_cell(int style, char c) {return (style << 8) | (0xff & c);}
static char cell_char(cell c) {return c & 0xff;}
static int cell_style(cell c) {return c >> 8;}

#define UPPER_SCREEN_BUFF_SIZE 256
#define SCREEN_BUFF_SIZE 8192
static char screen_buffer[SCREEN_BUFF_SIZE];  // aka window 0 (lower screen)
static char upper_screen_buffer[UPPER_SCREEN_BUFF_SIZE];  // aka window 1 (upper screen)

char* screen_buffer_ptr = screen_buffer;
char* upper_screen_buffer_ptr = upper_screen_buffer;

/* A cell's style is REVERSE_STYLE, normal (0), or PICTURE_STYLE.
 * PICTURE_STYLE means the character is part of an ascii image outline
 * box.  (This just buys us the ability to turn box display on and off
 * with immediate effect.  No, not very useful, but I wanted to give
 * the rv bit some company in that huge byte I allocated for it.)  */
#define PICTURE_STYLE 16

static int current_style = 0;

/* Which cells have changed (1 byte per cell).  */
static char *screen_changes;

static int cursor_row = 0, cursor_col = 0;

/* Compression styles.  */
static enum {
  COMPRESSION_NONE, COMPRESSION_SPANS, COMPRESSION_MAX,
} compression_mode = COMPRESSION_SPANS;
static char *compression_names[] = {"NONE", "SPANS", "MAX"};
static int hide_lines = 0;

/* Reverse-video display styles.  */
static enum {
  RV_NONE, RV_DOUBLESTRIKE, RV_UNDERLINE, RV_CAPS,
} rv_mode = RV_NONE;
static char *rv_names[] = {"NONE", "DOUBLESTRIKE", "UNDERLINE", "CAPS"};
static char rv_blank_char = ' ';

static cell *dumb_row(int r) {return screen_data + r * h_screen_cols;}

static char *dumb_changes_row(int r)
{
    return screen_changes + r * h_screen_cols;
}

int os_char_width (zchar z)
{
    if (plain_ascii && z >= ZC_LATIN1_MIN) {
	char *p = latin1_to_ascii + 4 * (z - ZC_LATIN1_MIN);
	return strchr(p, ' ') - p;
    }
    return 1;
}

int os_string_width (const zchar *s)
{
    int width = 0;
    zchar c;

    while ((c = *s++) != 0) {
	if (c == ZC_NEW_STYLE || c == ZC_NEW_FONT)
	    s++;
	else
	    width += os_char_width(c);
    }
    return width;
}

void os_set_cursor(int row, int col)
{
	//printf("\n--> win:%d\trow:%d\tcol:%d MAX_COLS:%d<--\n", cwin, row, col, h_screen_cols);
	if (cwin == 1 && row == 1) {
		upper_screen_buffer_ptr = upper_screen_buffer + (col-1);
	}

    cursor_row = row - 1; cursor_col = col - 1;  // 0-index
    if (cursor_row >= h_screen_rows)
	cursor_row = h_screen_rows - 1;
}

/* Set a cell and update screen_changes.  */
static void dumb_set_cell(int row, int col, cell c)
{
    dumb_changes_row(row)[col] = (c != dumb_row(row)[col]);
    dumb_row(row)[col] = c;
}

void dumb_set_picture_cell(int row, int col, char c)
{
    dumb_set_cell(row, col, make_cell(PICTURE_STYLE, c));
}

/* Copy a cell and copy its changedness state.
 * This is used for scrolling.  */
static void dumb_copy_cell(int dest_row, int dest_col,
			   int src_row, int src_col)
{
    dumb_row(dest_row)[dest_col] = dumb_row(src_row)[src_col];
    dumb_changes_row(dest_row)[dest_col] = dumb_changes_row(src_row)[src_col];
}

void os_set_text_style(int x)
{
    current_style = x & REVERSE_STYLE;
}

/* put a character in the cell at the cursor and advance the cursor.  */
static void dumb_display_char(char c)
{
	if (cwin == 1 && cursor_row == 0) {
		if ((upper_screen_buffer_ptr - upper_screen_buffer) < (UPPER_SCREEN_BUFF_SIZE - 1)) {
			*upper_screen_buffer_ptr++ = c;
		}
	}
	else {
		if ((screen_buffer_ptr - screen_buffer) < (SCREEN_BUFF_SIZE - 1)) {
			*screen_buffer_ptr++ = c;
		}
	}
}

void dumb_display_user_input(char *s)
{
    /* copy to screen without marking it as a change.  */
    /* while (*s) */
	/* dumb_row(cursor_row)[cursor_col++] = make_cell(0, *s++); */
}

void dumb_discard_old_input(int num_chars)
{
  /* Weird discard stuff.  Grep spec for 'pain in my butt'.  */
  /* The old characters should be on the screen just before the cursor.
   * Erase them.  */
    cursor_col -= num_chars;

    if (cursor_col < 0)
	cursor_col = 0;
    os_erase_area(cursor_row + 1, cursor_col + 1,
	cursor_row + 1, cursor_col + num_chars, -1);
}

void os_display_char (zchar c)
{
    if (c >= ZC_LATIN1_MIN) {
	if (plain_ascii) {
	    char *ptr = latin1_to_ascii + 4 * (c - ZC_LATIN1_MIN);
	    do
		dumb_display_char(*ptr++);
	    while (*ptr != ' ');
	} else
	    dumb_display_char(c);
    } else if (c >= 32 && c <= 126) {
	dumb_display_char(c);
    } else if (c == ZC_GAP) {
	dumb_display_char(' '); dumb_display_char(' ');
    } else if (c == ZC_INDENT) {
	dumb_display_char(' '); dumb_display_char(' '); dumb_display_char(' ');
    }
  return;
}


/* Haxor your boxor? */
void os_display_string (const zchar *s)
{
    zchar c;

    while ((c = *s++) != 0) {
	if (c == ZC_NEW_FONT)
	    s++;
	else if (c == ZC_NEW_STYLE)
	    os_set_text_style(*s++);
	else {
	    os_display_char (c);
	}
    }
}

void os_erase_area (int top, int left, int bottom, int right, int win)
{
    int row, col;
    top--; left--; bottom--; right--;
    for (row = top; row <= bottom; row++) {
	for (col = left; col <= right; col++)
	    dumb_set_cell(row, col, make_cell(current_style, ' '));
    }
}

void os_scroll_area (int top, int left, int bottom, int right, int units)
{
	if (cwin == 1) {
		if ((upper_screen_buffer_ptr - upper_screen_buffer) < (UPPER_SCREEN_BUFF_SIZE - 1)) {
			*upper_screen_buffer_ptr++ = '\n';
		}
	}
	else {
		if ((screen_buffer_ptr - screen_buffer) < (SCREEN_BUFF_SIZE - 1)) {
			*screen_buffer_ptr++ = '\n';
		}
	}
}

int os_font_data(int font, int *height, int *width)
{
    if (font == TEXT_FONT) {
	*height = 1; *width = 1; return 1;
    }
    return 0;
}

void os_set_colour (int UNUSED (x), int UNUSED (y)) {}
void os_set_font (int UNUSED (x)) {}

/* Print a cell to stdout.  */
static void show_cell(cell cel)
{
    char c = cell_char(cel);
    switch (cell_style(cel)) {
    case 0:
	putchar(c);
	break;
    case PICTURE_STYLE:
	putchar(show_pictures ? c : ' ');
	break;
    case REVERSE_STYLE:
	if (c == ' ')
	    putchar(rv_blank_char);
	else
	    switch (rv_mode) {
	    case RV_NONE: putchar(c); break;
	    case RV_CAPS: putchar(toupper(c)); break;
	    case RV_UNDERLINE: putchar('_'); putchar('\b'); putchar(c); break;
	    case RV_DOUBLESTRIKE: putchar(c); putchar('\b'); putchar(c); break;
	    }
	break;
    }
}

static bool will_print_blank(cell c)
{
    return (((cell_style(c) == PICTURE_STYLE) && !show_pictures)
	|| ((cell_char(c) == ' ')
	 && ((cell_style(c) != REVERSE_STYLE)
	|| (rv_blank_char == ' '))));
}

static void show_line_prefix(int row, char c)
{
    if (show_line_numbers)
	printf((row == -1) ? ".." : "%02d", (row + 1) % 100);
    if (show_line_types)
	putchar(c);
    /* Add a separator char (unless there's nothing to separate).  */
    if (show_line_numbers || show_line_types)
	putchar(' ');
}

/* Print a row to stdout.  */
static void show_row(int r)
{
    if (r == -1) {
	show_line_prefix(-1, '.');
    } else {
	int c, last;
	show_line_prefix(r, (r == cursor_row) ? ']' : ' ');
	/* Don't print spaces at end of line.  */
	/* (Saves bandwidth and printhead wear.)  */
	/* TODO: compress spaces to tabs.  */
	for (last = h_screen_cols - 1; last >= 0; last--)
	    if (!will_print_blank(dumb_row(r)[last]))
		break;
	for (c = 0; c <= last; c++)
	    show_cell(dumb_row(r)[c]);
    }
    // putchar('\n');
}

/* Print the part of the cursor row before the cursor.  */
void dumb_show_prompt(bool show_cursor, char line_type)
{
    int i;
    show_line_prefix(show_cursor ? cursor_row : -1, line_type);
    if (show_cursor) {
	for (i = 0; i < cursor_col; i++)
	    show_cell(dumb_row(cursor_row)[i]);
    }
}

static void mark_all_unchanged(void)
{
    memset(screen_changes, 0, screen_cells);
}

/* Check if a cell is a blank or will display as one.
 * (Used to help decide if contents are worth printing.)  */
static bool is_blank(cell c)
{
    return ((cell_char(c) == ' ')
	|| ((cell_style(c) == PICTURE_STYLE) && !show_pictures));
}

void dumb_clear_output(void)
{
  mark_all_unchanged();
}

/* Show the current screen contents, or what's changed since the last
 * call.
 *
 * If compressing, and show_cursor is true, and the cursor is past the
 * last nonblank character on the last line that would be shown, then
 * don't show that line (because it will be redundant with the prompt
 * line just below it).  */
void dumb_show_screen(bool show_cursor)
{
    int r, c, first, last;
    char changed_rows[0x100];

    /* Easy case */
    if (compression_mode == COMPRESSION_NONE) {
	for (r = hide_lines; r < h_screen_rows; r++)
	    show_row(r);
	mark_all_unchanged();
	return;
    }

    /* Check which rows changed, and where the first and last change is.  */
    first = last = -1;
    memset(changed_rows, 0, h_screen_rows);
    for (r = hide_lines; r < h_screen_rows; r++) {
	for (c = 0; c < h_screen_cols; c++)
	    if (dumb_changes_row(r)[c] && !is_blank(dumb_row(r)[c]))
		break;
	changed_rows[r] = (c != h_screen_cols);
	if (changed_rows[r]) {
	    first = (first != -1) ? first : r;
	    last = r;
	}
    }

    if (first == -1)
	return;

    /* The show_cursor rule described above */
    if (show_cursor && (cursor_row == last)) {
	for (c = cursor_col; c < h_screen_cols; c++)
	    if (!is_blank(dumb_row(last)[c]))
		break;
	if (c == h_screen_cols)
	    last--;
    }

    /* Display the appropriate rows.  */
    if (compression_mode == COMPRESSION_MAX) {
	for (r = first; r <= last; r++)
	    if (changed_rows[r])
		show_row(r);
    } else {
	/* COMPRESSION_SPANS */
	for (r = first; r <= last; r++) {
	    if (changed_rows[r] || changed_rows[r + 1])
		show_row(r);
	    else {
		while (!changed_rows[r + 1])
		    r++;
		show_row(-1);
	    }
	}
	if (show_cursor && (cursor_row > last + 1))
	    show_row((cursor_row == last + 2) ? (last + 1) : -1);
    }

    mark_all_unchanged();
}

/* Unconditionally show whole screen.  For \s user command.  */
void dumb_dump_screen(void)
{
    int r;
    for (r = 0; r < h_screen_height; r++)
	show_row(r);
}

/* Called when it's time for a more prompt but user has them turned off.  */
void dumb_elide_more_prompt(void)
{
    dumb_show_screen(FALSE);
    if (compression_mode == COMPRESSION_SPANS && hide_lines == 0) {
	show_row(-1);
    }
}

void os_reset_screen(void)
{
    dumb_show_screen(FALSE);
}

void os_beep (int volume)
{
    if (visual_bell)
	printf("[%s-PITCHED BEEP]\n", (volume == 1) ? "HIGH" : "LOW");
    else
	putchar('\a'); /* so much for dumb.  */
}


/* To make the common code happy */

void os_init_sound(void) {}
void os_prepare_sample (int UNUSED (a)) {}
void os_finish_with_sample (int UNUSED (a)) {}
void os_start_sample (int UNUSED (a), int UNUSED (b), int UNUSED (c), zword UNUSED (d)) {}
void os_stop_sample (int UNUSED (a)) {}


/* if val is '0' or '1', set *var accordingly, else toggle it.  */
static void toggle(bool *var, char val)
{
    *var = val == '1' || (val != '0' && !*var);
}

bool dumb_output_handle_setting(const char *setting, bool show_cursor,
				bool startup)
{
    char *p;
    int i;

    if (!strncmp(setting, "pb", 2)) {
	toggle(&show_pictures, setting[2]);
	printf("Picture outlines display %s\n", show_pictures ? "ON" : "OFF");
	if (startup)
	    return TRUE;
	for (i = 0; i < screen_cells; i++)
	    screen_changes[i] = (cell_style(screen_data[i]) == PICTURE_STYLE);
	dumb_show_screen(show_cursor);
    } else if (!strncmp(setting, "vb", 2)) {
	toggle(&visual_bell, setting[2]);
	printf("Visual bell %s\n", visual_bell ? "ON" : "OFF");
	os_beep(1); os_beep(2);
    } else if (!strncmp(setting, "ln", 2)) {
	toggle(&show_line_numbers, setting[2]);
	printf("Line numbering %s\n", show_line_numbers ? "ON" : "OFF");
    } else if (!strncmp(setting, "lt", 2)) {
	toggle(&show_line_types, setting[2]);
	printf("Line-type display %s\n", show_line_types ? "ON" : "OFF");

    } else if (*setting == 'c') {
	switch (setting[1]) {
	case 'm': compression_mode = COMPRESSION_MAX; break;
	case 's': compression_mode = COMPRESSION_SPANS; break;
	case 'n': compression_mode = COMPRESSION_NONE; break;
	case 'h': hide_lines = atoi(&setting[2]); break;
	default: return FALSE;
	}
	printf("Compression mode %s, hiding top %d lines\n",
	    compression_names[compression_mode], hide_lines);
    } else if (*setting == 'r') {
	switch (setting[1]) {
	case 'n': rv_mode = RV_NONE; break;
	case 'o': rv_mode = RV_DOUBLESTRIKE; break;
	case 'u': rv_mode = RV_UNDERLINE; break;
	case 'c': rv_mode = RV_CAPS; break;
	case 'b': rv_blank_char = setting[2] ? setting[2] : ' '; break;
	default: return FALSE;
	}
	printf("Reverse-video mode %s, blanks reverse to '%c': ",
	    rv_names[rv_mode], rv_blank_char);

	for (p = "sample reverse text"; *p; p++)
	    show_cell(make_cell(REVERSE_STYLE, *p));
	putchar('\n');
	for (i = 0; i < screen_cells; i++)
	    screen_changes[i] = (cell_style(screen_data[i]) == REVERSE_STYLE);
	dumb_show_screen(show_cursor);
    } else if (!strcmp(setting, "set")) {

	printf("Compression Mode %s, hiding top %d lines\n",
	    compression_names[compression_mode], hide_lines);
	printf("Picture Boxes display %s\n", show_pictures ? "ON" : "OFF");
	printf("Visual Bell %s\n", visual_bell ? "ON" : "OFF");
	os_beep(1); os_beep(2);
	printf("Line Numbering %s\n", show_line_numbers ? "ON" : "OFF");
	printf("Line-Type display %s\n", show_line_types ? "ON" : "OFF");
	printf("Reverse-Video mode %s, Blanks reverse to '%c': ",
	    rv_names[rv_mode], rv_blank_char);
	for (p = "sample reverse text"; *p; p++)
	    show_cell(make_cell(REVERSE_STYLE, *p));
	putchar('\n');
    } else
	return FALSE;
    return TRUE;
}

void dumb_init_output(void)
{
    if (h_version == V3) {
	h_config |= CONFIG_SPLITSCREEN;
	h_config |= CONFIG_NOSTATUSLINE;
	h_flags &= ~OLD_SOUND_FLAG;
    }

    if (h_version >= V5) {
	h_flags &= ~SOUND_FLAG;
    }

    h_screen_height = h_screen_rows;
    h_screen_width = h_screen_cols;
    screen_cells = h_screen_rows * h_screen_cols;

    h_font_width = 1; h_font_height = 1;

    if (show_line_types == -1)
	show_line_types = h_version > 3;

    if (screen_data == NULL) {
      screen_data = malloc(screen_cells * sizeof(cell));
    }
    if (screen_changes == NULL) {
      screen_changes = calloc(screen_cells, sizeof(char));
    }
    os_erase_area(1, 1, h_screen_rows, h_screen_cols, -2);
}

char* dumb_get_screen(void) {
  flush_buffer();
  *screen_buffer_ptr = '\0';
  return screen_buffer;
}

void dumb_clear_screen(void) {
  screen_buffer_ptr = screen_buffer;
}


char* dumb_get_lower_screen(void) {
  flush_buffer();
  *screen_buffer_ptr = '\0';
  return screen_buffer;
}

void dumb_clear_lower_screen(void) {
  screen_buffer_ptr = screen_buffer;
}

char* dumb_get_upper_screen(void) {
  upper_screen_buffer[UPPER_SCREEN_BUFF_SIZE-1] = '\0';
  return upper_screen_buffer;
}

void dumb_clear_upper_screen(void) {
  upper_screen_buffer_ptr = upper_screen_buffer;
}

void dumb_free(void) {
	if (screen_data) {
      free(screen_data);
	  screen_data = NULL;
    }
    if (screen_changes) {
      free(screen_changes);
	  screen_changes = NULL;
    }
}
