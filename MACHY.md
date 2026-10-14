# SketchyBar — the `machy` branch

This is a fork of [FelixKratz/SketchyBar](https://github.com/FelixKratz/SketchyBar)
carrying the changes [machy](https://github.com/DanteCpp/machy) needs to render
its popup cards. machy is a macOS port of [Omarchy](https://omarchy.org)'s
desktop, and its bar popups are a port of Omarchy's quickshell "pole cards" —
the battery, audio, network, bluetooth and agents panels.

Upstream sketchybar lays a popup out as a single column: one item, one row, no
cap on height. Three things in those reference panels do not fit that model,
and this branch adds them. Everything is additive and defaults to upstream
behaviour, so an unmodified sketchybarrc renders exactly as before.

## `inline` — more than one item per popup row

```
sketchybar --set my.item inline=on
```

An item with `inline=on` is laid out on the row its predecessor opened instead
of starting a row of its own; the row's height is the tallest item on it. That
turns the column into a grid, which is what a row of buttons (Omarchy's power
profiles, DNS providers, agent provider switch) or a label/value pair needs.

Only meaningful for items in a popup. A horizontal popup is one row by
definition and is unaffected.

## `popup.max_height` — a capped, scrollable popup

```
sketchybar --set my.item popup.max_height=760 popup.scroll_step=2
```

A popup whose content is taller than `max_height` is clipped to it, and the
wheel scrolls the rows past the cap. Without it a long device list simply grew
off the bottom of the screen and the overflow was unreachable.

Scrolling snaps to whole rows. sketchybar draws every item in its own window
and clips nothing, so a half-scrolled row would spill its text outside the
popup box and over the bar; snapping keeps every visible row whole.

* `popup.max_height` — cap in points. `0` (the default) means no cap.
* `popup.scroll_step` — rows moved per wheel tick, default `1`.
* `popup.scroll_offset` — index of the first visible row; settable, clamped so
  the last page is always full, and reset whenever the popup opens.
* `--query` reports `max_height`, `content_height`, `scroll_offset` and
  `scroll_step` under `popup`.

A row that has subscribed to `mouse.scrolled` keeps the wheel for itself — a
volume slider still changes the volume rather than scrolling the card.

### `scrollable` — keep popup chrome fixed

```
sketchybar --set popup.network.list.1 scrollable=on
```

When at least one popup row is marked `scrollable=on`, only the contiguous row
region from the first marked row through the last one participates in popup
scrolling. Rows before it (headers, stats and actions) and after it (the card's
bottom inset) remain fixed. With no marked rows, `popup.max_height` retains its
original whole-card scrolling behavior for compatibility.

Popup items may also set `cell_height=<points>` to override the popup's normal
row floor for that row. Machy uses it for exact top/bottom insets and divider
rows; ordinary items keep the inherited popup height.

## `background.fill` — a share bar behind a row

```
sketchybar --set my.item background.fill=63 background.fill_color=0x24cdd6f4
```

Paints the leading `fill` percent (0–100, default 100) of the item's background
box in `fill_color`, clipped to the background's corner radius and drawn over
`background.color`. It lets a row carry a progress or share bar *behind* its own
text, with no second item and no change to the row's width — the layout the
reference's "tokens by model" table uses.

## Slider hit area

Upstream hit-tests a slider click against the track's own bounds. A 4pt
hairline track — what these cards use — is unhittable in practice, so the hit
test now takes the slider's horizontal span at any height within the row. The
row you can see is the row you can grab; `click_script` still receives the new
value in `$PERCENTAGE`.

## `popup.display` — open without moving application focus

`popup.display=mouse` captures the display under the pointer when the command
is processed. Subsequent refreshes keep the card on that physical display,
without focusing an application or waiting for a display-focus notification.
`popup.display=active` restores the default behavior. An available arrangement
index (for example `popup.display=2`) explicitly selects a display.

Nested popups inherit the outer card's display. If the selected monitor is
removed, routing falls back to the active display. The query field
`popup.display_id` reports the selected physical display ID (0 means active).

Validation: `make clean && make arm64 && python3 tests/popup-display.py`.
The test briefly creates a separate transparent bar and exercises every
connected display without moving the pointer or changing application focus.

## Building

```
make            # universal binary in ./bin/sketchybar
make arm64      # or a single arch
```

The build ad-hoc signs the binary (`codesign --sign - --identifier sketchybar`).
That is not cosmetic: without it the linker's automatic "linker-signed"
signature is all the binary has, and macOS TCC treats those as ephemeral — it
will not PERSIST a permission grant against one. A bar that polls Bluetooth or
Location then re-prompts on every poll, forever. Homebrew ad-hoc signs
upstream's bottle for the same reason.

Licensed GPL-3.0-only, like upstream.
