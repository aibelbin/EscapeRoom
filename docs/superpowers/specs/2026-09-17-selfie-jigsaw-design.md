# Selfie Jigsaw (Challenge 03) Design

Date: 2026-09-17
Status: approved

## Problem

The sliding 3×3 is too hard for the party. Challenge 03 stays a selfie station, but the puzzle becomes a 3×3 square-piece jigsaw: empty board, tray of pieces, drag to place. Pose, dribble, laser maze, server, camera fallback, and `progress.json` stay as they are.

## Scope

In:

- Replace the sliding engine and play UI in `challenges/03-selfie-puzzle`
- 3×3 square pieces cut from the snapped selfie (or fallback photo)
- Empty board + shuffled tray; pointer-event drag; snap into cells
- Rewrite Node puzzle tests; station README and root README copy
- Keep `SELFIE STATION CLEAR`, `POST /complete`, `id: "selfie"`

Out:

- Interlocking / irregular jigsaw shapes
- Network, dashboard, pose/dribble/laser changes
- HTML5 drag-and-drop API
- Changing the Python server beyond what the page already needs

## Game flow

1. Idle polaroid + live preview (or fallback). **Start** unchanged.
2. Start snaps a square mirrored crop (or uses the fallback photo).
3. Play: empty 3×3 board in the polaroid frame. Nine square pieces in a tray under the board, shuffled, showing selfie fragments. No hole.
4. Drag a piece onto a cell. It snaps into that cell.
5. Drop on an occupied cell: the two pieces swap. Drop on the same cell: no-op.
6. Drop on the tray or anywhere off the board: the piece goes to the tray.
7. Pointer cancel: the piece returns to where the drag started (tray or previous cell).
8. Pieces stay movable until solved.
9. Solved when every cell `i` holds piece `i` (row-major, same as today’s tile IDs). Green overlay `SELFIE STATION CLEAR`, `POST /complete` once.
10. **Again** returns to idle and takes a new photo for the next guest.

No arrow-key sliding. Click-to-slide is gone.

## State model

`SIZE = 3`. Pieces are integers `0..8`. Piece `i` belongs in board slot `i`.

```
board: (number | null)[9]   // null = empty slot
tray: number[]              // pieces not on the board, order is display order
```

Start of a round: `board` is nine `null`s. `tray` is a shuffle of `0..8` that is not already the identity order (so the tray is visibly scrambled even before anyone places).

Operations (pure, return new state):

- `place(state, pieceId, slot)` — piece must be in the tray or on another slot. Target empty → occupy. Target occupied → swap. Piece leaves the tray if it came from there.
- `returnToTray(state, pieceId)` — piece leaves its slot (if any) and appends to the tray.
- `isSolved(state)` — true iff `board[i] === i` for all `i`.

Shuffle uses a seeded-optional RNG so tests are deterministic.

## UI

Pointer events, not HTML5 DnD: `pointerdown` on a piece, ghost follows the pointer, `pointerup` hit-tests board cells. Trackpad and mouse. Touch works if the laptop has it.

Idle, fallback (`?fallback=1` and auto-fallback), green clear overlay, and **Again** stay. Headline stays “Put yourself back together”. No move counter.

## Error handling

- Camera / `getUserMedia` / hung preview: existing fallback path.
- `POST /complete` fails: existing “Solved, but progress file did not save.”
- Drop on tray or off the board: piece goes to the tray.
- Pointer cancel: piece returns to drag origin.
- Missing camera does not crash the Python server.

## Testing

Automated (no webcam):

- Fresh round: board empty, tray has `{0..8}`, not identity order
- Place from tray onto empty slot
- Swap two placed pieces
- Return a placed piece to the tray
- `isSolved` false until all nine match; true when they do
- Existing Python `test_progress.py`

Manual: snap, assemble, green + `progress.json`, **Again**, `?fallback=1`.

## Constraints

- All local. Python 3.12 stdlib server, Node for JS tests.
- Do not change pose, dribble, or laser maze.
- No git commits unless asked.
