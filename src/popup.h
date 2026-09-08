#pragma once
#include "background.h"
#include "misc/helpers.h"
#include "window.h"

struct bar_item;
struct bar;

struct popup {
  bool drawing;
  bool horizontal;
  bool overrides_cell_size;
  bool mouse_over;
  bool needs_ordering;
  bool topmost;

  char align;

  uint32_t adid;
  uint32_t cell_size;
  uint32_t blur_radius;
  int y_offset;

  // machy fork: a popup taller than max_height is clipped to it and scrolls.
  // content_height is the unclipped height of the stacked rows, scroll_offset
  // how far the content is pushed up, both in points.
  uint32_t max_height;
  uint32_t content_height;
  uint32_t scroll_step;
  int scroll_offset;

  CGPoint anchor;
  struct window window;

  struct bar_item* host;
  struct bar_item** items;
  uint32_t num_items;

  struct background background;
};

void popup_init(struct popup* popup, struct bar_item* host);
void popup_set_anchor(struct popup* popup, CGPoint anchor, uint32_t adid);
void popup_add_item(struct popup* popup, struct bar_item* item);
bool popup_set_drawing(struct popup* popup, bool drawing);
void popup_remove_item(struct popup* popup, struct bar_item* bar_item);

void popup_clear_pointers(struct popup* popup);

uint32_t popup_get_width(struct popup* popup);
void popup_calculate_bounds(struct popup* popup, struct bar* bar);
void popup_draw(struct popup* popup);
void popup_destroy(struct popup* popup);

void popup_change_space(struct popup* popup, uint64_t dsid, uint32_t adid);
bool popup_is_scrollable(struct popup* popup);
bool popup_scroll(struct popup* popup, int delta);
void popup_reset_scroll(struct popup* popup);
void popup_serialize(struct popup* popup, char* indent, FILE* rsp);
bool popup_parse_sub_domain(struct popup* popup, FILE* rsp, struct token property, char* message);
