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
