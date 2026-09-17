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
