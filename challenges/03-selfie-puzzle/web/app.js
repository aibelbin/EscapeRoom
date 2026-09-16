import { EMPTY, SIZE, canSlide, createSolved, isSolved, slide, shuffle } from "./puzzle.js";

const FALLBACK = "/assets/fallback.png";
const preview = document.querySelector("#preview");
const fallbackPreview = document.querySelector("#fallbackPreview");
const startBtn = document.querySelector("#start");
const againBtn = document.querySelector("#again");
const idle = document.querySelector("#idle");
const play = document.querySelector("#play");
const boardEl = document.querySelector("#board");
const movesEl = document.querySelector("#moves");
const statusEl = document.querySelector("#status");
const clearEl = document.querySelector("#clear");
const headline = document.querySelector("#headline");

let stream = null;
let usingFallback = false;
let photoUrl = FALLBACK;
let board = createSolved();
let moves = 0;
let wrote = false;

function showStatus(text) {
  statusEl.hidden = !text;
  statusEl.textContent = text;
}

function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error("timeout")), ms);
    }),
  ]);
}

async function startCamera() {
  if (!navigator.mediaDevices?.getUserMedia) {
    return false;
  }
  try {
    stream = await withTimeout(
      navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user" },
        audio: false,
      }),
      2500,
    );
    preview.srcObject = stream;
    await preview.play();
    await waitForVideo(preview, 2000);
    return preview.videoWidth > 0;
  } catch {
    return false;
  }
}

function waitForVideo(video, ms) {
  return new Promise((resolve) => {
    if (video.readyState >= 2 && video.videoWidth > 0) {
      resolve();
      return;
    }
    const t = setTimeout(() => resolve(), ms);
    video.addEventListener(
      "loadeddata",
      () => {
        clearTimeout(t);
        resolve();
      },
      { once: true },
    );
  });
}

function useFallback(reason) {
  usingFallback = true;
  stopCamera();
  preview.hidden = true;
  fallbackPreview.hidden = false;
  fallbackPreview.src = FALLBACK;
  photoUrl = FALLBACK;
  showStatus(reason);
}

function stopCamera() {
  if (stream) {
    for (const track of stream.getTracks()) {
      track.stop();
    }
    stream = null;
  }
  preview.srcObject = null;
}

function snapFromVideo() {
  const size = 640;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d");
  const vw = preview.videoWidth;
  const vh = preview.videoHeight;
  const side = Math.min(vw, vh);
  const sx = (vw - side) / 2;
  const sy = (vh - side) / 2;
  ctx.translate(size, 0);
  ctx.scale(-1, 1);
  ctx.drawImage(preview, sx, sy, side, side, 0, 0, size, size);
  return canvas.toDataURL("image/jpeg", 0.92);
}

function tilePosition(tileId) {
  const row = Math.floor(tileId / SIZE);
  const col = tileId % SIZE;
  const pct = SIZE === 1 ? 0 : 100 / (SIZE - 1);
  return `${col * pct}% ${row * pct}%`;
}

function render() {
  boardEl.replaceChildren();
  board.forEach((tileId, index) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "tile" + (tileId === EMPTY ? " empty" : "");
    btn.setAttribute("role", "gridcell");
    if (tileId !== EMPTY) {
      btn.style.backgroundImage = `url("${photoUrl}")`;
      btn.style.backgroundSize = `${SIZE * 100}% ${SIZE * 100}%`;
      btn.style.backgroundPosition = tilePosition(tileId);
      btn.setAttribute("aria-label", `Tile ${tileId + 1}`);
      btn.addEventListener("click", () => trySlide(index));
    } else {
      btn.tabIndex = -1;
      btn.setAttribute("aria-label", "Empty");
    }
    boardEl.append(btn);
  });
  movesEl.textContent = `${moves} ${moves === 1 ? "move" : "moves"}`;
}

function trySlide(index) {
  if (!canSlide(board, index)) {
    return;
  }
  board = slide(board, index);
  moves += 1;
  render();
  if (isSolved(board)) {
    onSolved();
  }
}

async function onSolved() {
  headline.textContent = "That's you.";
  clearEl.hidden = false;
  if (!wrote) {
    try {
      await fetch("/complete", { method: "POST" });
      wrote = true;
    } catch {
      showStatus("Solved, but progress file did not save.");
    }
  }
}

function beginPuzzle(url) {
  photoUrl = url;
  board = shuffle(createSolved(), 80);
  moves = 0;
  wrote = false;
  idle.hidden = true;
  play.hidden = false;
  clearEl.hidden = true;
  headline.textContent = "Put yourself back together";
  render();
}

async function onStart() {
  startBtn.disabled = true;
  if (usingFallback || !preview.srcObject || preview.videoWidth === 0) {
    beginPuzzle(FALLBACK);
    startBtn.disabled = false;
    return;
  }
  try {
    beginPuzzle(snapFromVideo());
  } catch {
    useFallback("Using fallback photo");
    beginPuzzle(FALLBACK);
  }
  startBtn.disabled = false;
}

function onAgain() {
  clearEl.hidden = true;
  play.hidden = true;
  idle.hidden = false;
  wrote = false;
  headline.textContent = "Put yourself back together";
  boot();
}

function onKey(event) {
  if (play.hidden || !clearEl.hidden) {
    return;
  }
  const empty = board.indexOf(EMPTY);
  const row = Math.floor(empty / SIZE);
  const col = empty % SIZE;
  let target = null;
  if (event.key === "ArrowLeft" && col < SIZE - 1) target = empty + 1;
  if (event.key === "ArrowRight" && col > 0) target = empty - 1;
  if (event.key === "ArrowUp" && row < SIZE - 1) target = empty + SIZE;
  if (event.key === "ArrowDown" && row > 0) target = empty - SIZE;
  if (target !== null) {
    event.preventDefault();
    trySlide(target);
  }
}

async function boot() {
  showStatus("");
  preview.hidden = false;
  fallbackPreview.hidden = true;
  usingFallback = false;
  const forceFallback = new URLSearchParams(location.search).has("fallback");
  if (forceFallback) {
    useFallback("Using fallback photo");
    return;
  }
  const ok = await startCamera();
  if (!ok) {
    useFallback("Using fallback photo");
  }
}

startBtn.addEventListener("click", onStart);
againBtn.addEventListener("click", onAgain);
window.addEventListener("keydown", onKey);
boot();
