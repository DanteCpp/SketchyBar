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

## Building

```
make            # universal binary in ./bin/sketchybar
make arm64      # or a single arch
```

Licensed GPL-3.0-only, like upstream.
