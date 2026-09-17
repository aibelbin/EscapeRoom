# Selfie Jigsaw Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the sliding 3×3 in challenge 03 with a tray-and-board square jigsaw, keeping the selfie snap, fallback, green clear, and `progress.json`.

**Architecture:** Pure puzzle state in `puzzle.js` (`board` of 9 slots, `tray` of leftover pieces, `place` / `returnToTray` / `isSolved`). `app.js` owns camera, pointer-event drag, and rendering. Python server is unchanged.

**Tech Stack:** Browser JS modules, Node test runner, stdlib Python 3.12 server, existing CSS.

## Global Constraints

- All local. Do not change pose, dribble, or laser maze.
- `SIZE = 3`. Piece `i` belongs in board slot `i`.
- Pointer events, not HTML5 drag-and-drop.
- Green overlay copy stays `SELFIE STATION CLEAR`. Progress `id` stays `"selfie"`.
- No git commits unless the user asks.
- Python 3.12 stdlib server, Node for JS tests.

---

## File map

- Modify: `challenges/03-selfie-puzzle/web/puzzle.js` — jigsaw state
- Modify: `challenges/03-selfie-puzzle/tests/puzzle.test.js` — engine tests
- Modify: `challenges/03-selfie-puzzle/web/index.html` — tray, drop move counter
- Modify: `challenges/03-selfie-puzzle/web/style.css` — board cells + tray
- Modify: `challenges/03-selfie-puzzle/web/app.js` — drag UI, drop sliding
- Modify: `challenges/03-selfie-puzzle/README.md`
- Modify: `README.md` — challenge 3 copy
- Leave: `main.py`, `progress.py`, `tests/test_progress.py`

---

### Task 1: Jigsaw state engine

**Files:**
- Modify: `challenges/03-selfie-puzzle/tests/puzzle.test.js`
- Modify: `challenges/03-selfie-puzzle/web/puzzle.js`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `SIZE = 3`
  - `emptyBoard() -> (number|null)[]`
  - `createRound(rng = Math.random) -> { board, tray }`
  - `place(state, pieceId, slot) -> { board, tray }`
  - `returnToTray(state, pieceId) -> { board, tray }`
  - `isSolved(state) -> boolean`

- [ ] **Step 1: Write the failing tests**

Replace `challenges/03-selfie-puzzle/tests/puzzle.test.js` with:

```js
import test from "node:test";
import assert from "node:assert/strict";
import {
  SIZE,
  createRound,
  isSolved,
  place,
  returnToTray,
} from "../web/puzzle.js";

const seq = (n) => {
  let i = 0;
  return () => {
    i += 1;
    return (i % n) / n;
  };
};

test("fresh round has an empty board and every piece in the tray", () => {
  const state = createRound(seq(9));
  assert.equal(state.board.length, SIZE * SIZE);
  assert.equal(state.board.every((cell) => cell === null), true);
  assert.equal(new Set(state.tray).size, 9);
  assert.deepEqual([...state.tray].sort((a, b) => a - b), [0, 1, 2, 3, 4, 5, 6, 7, 8]);
  assert.equal(isSolved(state), false);
  assert.notDeepEqual(state.tray, [0, 1, 2, 3, 4, 5, 6, 7, 8]);
});

test("place from tray occupies an empty slot", () => {
  const start = createRound(seq(9));
  const piece = start.tray[0];
  const next = place(start, piece, 4);
  assert.equal(next.board[4], piece);
  assert.equal(next.tray.includes(piece), false);
  assert.equal(isSolved(next), false);
});

test("place onto an occupied slot swaps", () => {
  let state = createRound(seq(9));
  const a = state.tray[0];
  const b = state.tray[1];
  state = place(state, a, 0);
  state = place(state, b, 1);
  const swapped = place(state, a, 1);
  assert.equal(swapped.board[0], b);
  assert.equal(swapped.board[1], a);
});

test("returnToTray clears the slot and appends the piece", () => {
  let state = createRound(seq(9));
  const piece = state.tray[0];
  state = place(state, piece, 2);
  const next = returnToTray(state, piece);
  assert.equal(next.board[2], null);
  assert.equal(next.tray.at(-1), piece);
});

test("isSolved only when every slot holds its piece", () => {
  let state = createRound(() => 0.9);
  for (let i = 0; i < 8; i += 1) {
    state = place(state, i, i);
    assert.equal(isSolved(state), false);
  }
  state = place(state, 8, 8);
  assert.equal(isSolved(state), true);
});
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd challenges/03-selfie-puzzle && node --test tests/puzzle.test.js`

Expected: FAIL (old sliding exports / missing `createRound`)

- [ ] **Step 3: Write minimal implementation**

Replace `challenges/03-selfie-puzzle/web/puzzle.js` with:

```js
export const SIZE = 3;
const COUNT = SIZE * SIZE;

export function emptyBoard() {
  return Array.from({ length: COUNT }, () => null);
}

function shuffle(list, rng) {
  const next = list.slice();
  for (let i = next.length - 1; i > 0; i -= 1) {
    const j = Math.floor(rng() * (i + 1)) % (i + 1);
    [next[i], next[j]] = [next[j], next[i]];
  }
  return next;
}

function scrambleTray(rng) {
  const ids = Array.from({ length: COUNT }, (_, i) => i);
  let tray = shuffle(ids, rng);
  let guard = 0;
  while (tray.every((id, i) => id === i) && guard < 8) {
    tray = shuffle(ids, rng);
    guard += 1;
  }
  if (tray.every((id, i) => id === i)) {
    [tray[0], tray[1]] = [tray[1], tray[0]];
  }
  return tray;
}

export function createRound(rng = Math.random) {
  return { board: emptyBoard(), tray: scrambleTray(rng) };
}

export function isSolved(state) {
  return state.board.length === COUNT && state.board.every((piece, i) => piece === i);
}

function removeFromTray(tray, pieceId) {
  return tray.filter((id) => id !== pieceId);
}

export function place(state, pieceId, slot) {
  const board = state.board.slice();
  let tray = state.tray.slice();
  if (slot < 0 || slot >= COUNT) {
    return { board, tray };
  }
  const fromSlot = board.indexOf(pieceId);
  const inTray = tray.includes(pieceId);
  if (fromSlot < 0 && !inTray) {
    return { board, tray };
  }
  if (fromSlot === slot) {
    return { board, tray };
  }
  const occupant = board[slot];
  if (fromSlot >= 0) {
    board[fromSlot] = occupant;
  } else {
    tray = removeFromTray(tray, pieceId);
    if (occupant !== null) {
      tray.push(occupant);
    }
  }
  board[slot] = pieceId;
  return { board, tray };
}

export function returnToTray(state, pieceId) {
  const board = state.board.slice();
  const tray = state.tray.slice();
  const fromSlot = board.indexOf(pieceId);
  if (fromSlot >= 0) {
    board[fromSlot] = null;
  }
  if (!tray.includes(pieceId)) {
    tray.push(pieceId);
  }
  return { board, tray };
}
```

Note: `place` from tray onto an occupied slot should **swap** per spec. The block above sends the occupant to the tray, which is wrong for board-to-board vs tray-to-occupied.

Correct swap rule:

- Piece on board → occupied slot: swap the two board cells. Tray unchanged.
- Piece in tray → occupied slot: occupant goes to tray, piece occupies slot. That is a swap with the tray, which matches “drop on occupied cell swaps” when the incoming piece is from the tray.

Keep that behavior. The implementation above already does board-to-board swap via `board[fromSlot] = occupant`, and tray-to-occupied via `tray.push(occupant)`. That matches the spec.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd challenges/03-selfie-puzzle && node --test tests/puzzle.test.js`

Expected: PASS all 5 tests

- [ ] **Step 5: Commit**

Skip unless the user asks.

---

### Task 2: Drag UI

**Files:**
- Modify: `challenges/03-selfie-puzzle/web/index.html`
- Modify: `challenges/03-selfie-puzzle/web/style.css`
- Modify: `challenges/03-selfie-puzzle/web/app.js`

**Interfaces:**
- Consumes: `SIZE`, `createRound`, `place`, `returnToTray`, `isSolved` from `puzzle.js`
- Produces: pointer-drag play screen (board + tray), existing camera/fallback/clear

- [ ] **Step 1: Update HTML**

Replace the play section in `challenges/03-selfie-puzzle/web/index.html` so it is:

```html
      <section id="play" class="panel" hidden>
        <div id="board" class="board" role="grid" aria-label="Jigsaw board"></div>
        <div id="tray" class="tray" aria-label="Puzzle pieces"></div>
      </section>
```

Remove `#moves`. Keep idle polaroid, clear overlay, script tag.

- [ ] **Step 2: Update CSS**

In `challenges/03-selfie-puzzle/web/style.css`:

- Delete `.moves`
- Keep `.board` as 3×3 grid
- Add empty slot look (dark well)
- Add `.tray` as a wrapping row of smaller squares under the board
- Add `.piece` (selfie crop, `touch-action: none`)
- Add `.piece.dragging` (fixed ghost following the pointer, `pointer-events: none`)

`.tray` width matches the panel. Pieces in the tray use the same background-size/position math as board pieces.

- [ ] **Step 3: Rewrite play logic in `app.js`**

Keep camera, fallback, snap, `onSolved` / `POST /complete`, **Again**, `boot`.

Remove: `EMPTY`, `canSlide`, `slide`, `shuffle`, `createSolved`, `trySlide`, `onKey`, `moves`.

Play state:

```js
let puzzle = createRound();
```

`render()`:
- 9 board cells (`data-slot="0"..8"`). If occupied, render a `.piece` with selfie crop.
- Tray: one `.piece` per `puzzle.tray` id.

`pieceStyle(id)`: same `backgroundImage` / `backgroundSize` / `backgroundPosition` as the old tiles.

Drag:
- `pointerdown` on `.piece` → set `pointer capture`, mark dragging, record `pieceId` and origin
- `pointermove` → position a ghost at the pointer
- `pointerup` / `pointercancel`:
  - `elementFromPoint` → closest `[data-slot]` → `puzzle = place(puzzle, pieceId, slot)`
  - else → `puzzle = returnToTray(puzzle, pieceId)` (off-board / tray)
  - `pointercancel` instead restores the previous `puzzle` snapshot (drag origin)
- After a successful drop, `render()`; if `isSolved(puzzle)`, `onSolved()`

Do not start a new drag after the clear overlay is shown.

- [ ] **Step 4: Manual check**

Run: `cd challenges/03-selfie-puzzle && python3.12 main.py`

Open `http://127.0.0.1:8765/?fallback=1`, Start, drag pieces onto the board, swap, drop one back to the tray, solve, confirm green and `progress.json`.

- [ ] **Step 5: Commit**

Skip unless the user asks.

---

### Task 3: Docs + verify

**Files:**
- Modify: `challenges/03-selfie-puzzle/README.md`
- Modify: `README.md`

**Interfaces:**
- Consumes: shipped jigsaw behavior
- Produces: operator copy that says jigsaw, not sliding

- [ ] **Step 1: Station README**

How it plays:

1. Live preview / fallback
2. **Start** snaps a square crop and cuts it into 9 squares in a tray
3. Drag pieces onto the empty 3×3 board. Occupied cell swaps. Off the board returns to the tray.
4. Green `SELFIE STATION CLEAR` + `progress.json`
5. **Again** for the next guest

Controls: drag (trackpad/mouse). No arrow keys.

Fallback still `?fallback=1`. Tests: `node --test tests/puzzle.test.js` and pytest progress.

- [ ] **Step 2: Root README challenge 3 section**

Replace sliding copy with: empty board, tray of nine selfie squares, drag to place. Same launch command.

- [ ] **Step 3: Run automated tests**

```bash
cd challenges/03-selfie-puzzle && node --test tests/puzzle.test.js
cd challenges/03-selfie-puzzle && python3.12 -m pytest tests/test_progress.py -v
```

Expected: all pass.

- [ ] **Step 4: Commit**

Skip unless the user asks.
