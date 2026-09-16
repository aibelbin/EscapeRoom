export const SIZE = 3;
export const EMPTY = SIZE * SIZE - 1;

export function createSolved() {
  return Array.from({ length: SIZE * SIZE }, (_, i) => i);
}

export function isSolved(board) {
  return board.every((tile, i) => tile === i);
}

export function emptyIndex(board) {
  return board.indexOf(EMPTY);
}

function rc(index) {
  return { row: Math.floor(index / SIZE), col: index % SIZE };
}

export function canSlide(board, tileIndex) {
  const empty = emptyIndex(board);
  if (tileIndex < 0 || tileIndex >= board.length || tileIndex === empty) {
    return false;
  }
  const a = rc(tileIndex);
  const b = rc(empty);
  const dist = Math.abs(a.row - b.row) + Math.abs(a.col - b.col);
  return dist === 1;
}

export function slide(board, tileIndex) {
  if (!canSlide(board, tileIndex)) {
    return board.slice();
  }
  const next = board.slice();
  const empty = emptyIndex(next);
  [next[tileIndex], next[empty]] = [next[empty], next[tileIndex]];
  return next;
}

export function neighborsOfEmpty(board) {
  const empty = emptyIndex(board);
  const { row, col } = rc(empty);
  const spots = [
    [row - 1, col],
    [row + 1, col],
    [row, col - 1],
    [row, col + 1],
  ];
  return spots
    .filter(([r, c]) => r >= 0 && r < SIZE && c >= 0 && c < SIZE)
    .map(([r, c]) => r * SIZE + c);
}

export function shuffle(board, moves = 80, rng = Math.random) {
  let next = board.slice();
  for (let i = 0; i < moves; i += 1) {
    const options = neighborsOfEmpty(next);
    const pick = options[Math.floor(rng() * options.length) % options.length];
    next = slide(next, pick);
  }
  let extra = 0;
  while (isSolved(next) && extra < 16) {
    const options = neighborsOfEmpty(next);
    next = slide(next, options[0]);
    extra += 1;
  }
  return next;
}
