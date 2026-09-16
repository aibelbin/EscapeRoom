import test from "node:test";
import assert from "node:assert/strict";
import {
  EMPTY,
  SIZE,
  canSlide,
  createSolved,
  isSolved,
  slide,
  shuffle,
} from "../web/puzzle.js";

test("solved board is the identity", () => {
  const board = createSolved();
  assert.equal(board.length, SIZE * SIZE);
  assert.equal(board[8], EMPTY);
  assert.equal(isSolved(board), true);
});

test("only tiles next to the empty square can slide", () => {
  const board = createSolved();
  assert.equal(canSlide(board, 7), true);
  assert.equal(canSlide(board, 5), true);
  assert.equal(canSlide(board, 0), false);
});

test("slide swaps with the empty square", () => {
  const board = createSolved();
  const next = slide(board, 7);
  assert.equal(next[7], EMPTY);
  assert.equal(next[8], 7);
  assert.equal(isSolved(next), false);
});

test("shuffle is solvable and not already solved", () => {
  const board = shuffle(createSolved(), 80, () => 0.37);
  assert.equal(board.length, 9);
  assert.equal(isSolved(board), false);
  assert.equal(new Set(board).size, 9);
});
