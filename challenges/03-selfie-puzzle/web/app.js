import { SIZE, createRound, isSolved, place, returnToTray } from "./puzzle.js";

const FALLBACK = "/assets/fallback.png";
const preview = document.querySelector("#preview");
const fallbackPreview = document.querySelector("#fallbackPreview");
const startBtn = document.querySelector("#start");
const againBtn = document.querySelector("#again");
const idle = document.querySelector("#idle");
const play = document.querySelector("#play");
const boardEl = document.querySelector("#board");
const trayEl = document.querySelector("#tray");
const statusEl = document.querySelector("#status");
const clearEl = document.querySelector("#clear");
const headline = document.querySelector("#headline");

let stream = null;
let usingFallback = false;
let photoUrl = FALLBACK;
let puzzle = createRound();
let wrote = false;
let drag = null;

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

function pieceStyle(el, id) {
  el.style.backgroundImage = `url("${photoUrl}")`;
  el.style.backgroundSize = `${SIZE * 100}% ${SIZE * 100}%`;
  el.style.backgroundPosition = tilePosition(id);
}

function makePiece(id) {
  const el = document.createElement("button");
  el.type = "button";
  el.className = "piece";
  el.dataset.piece = String(id);
  el.setAttribute("aria-label", `Piece ${id + 1}`);
  pieceStyle(el, id);
  el.addEventListener("pointerdown", onPointerDown);
  return el;
}

function render() {
  boardEl.replaceChildren();
  puzzle.board.forEach((pieceId, slot) => {
    const cell = document.createElement("div");
    cell.className = "slot";
    cell.dataset.slot = String(slot);
    cell.setAttribute("role", "gridcell");
    if (pieceId !== null) {
      cell.append(makePiece(pieceId));
    }
    boardEl.append(cell);
  });
  trayEl.replaceChildren();
  puzzle.tray.forEach((pieceId) => {
    trayEl.append(makePiece(pieceId));
  });
}

function snapshot(state) {
  return { board: state.board.slice(), tray: state.tray.slice() };
}

function onPointerDown(event) {
  if (event.button !== 0 || !clearEl.hidden || drag) {
    return;
  }
  const el = event.currentTarget;
  const pieceId = Number(el.dataset.piece);
  el.setPointerCapture(event.pointerId);
  const size = el.getBoundingClientRect().width;
  el.style.setProperty("--drag-size", `${size}px`);
  el.classList.add("dragging");
  drag = {
    pieceId,
    origin: snapshot(puzzle),
    el,
    pointerId: event.pointerId,
  };
  moveGhost(event);
  window.addEventListener("pointermove", onPointerMove);
  window.addEventListener("pointerup", onPointerUp);
  window.addEventListener("pointercancel", onPointerCancel);
  event.preventDefault();
}

function moveGhost(event) {
  if (!drag) {
    return;
  }
  const size = Number.parseFloat(drag.el.style.getPropertyValue("--drag-size")) || 80;
  drag.el.style.left = `${event.clientX - size / 2}px`;
  drag.el.style.top = `${event.clientY - size / 2}px`;
}

function onPointerMove(event) {
  if (!drag || event.pointerId !== drag.pointerId) {
    return;
  }
  moveGhost(event);
}

function dropTarget(event) {
  const ghost = drag?.el;
  if (ghost) {
    ghost.style.visibility = "hidden";
  }
  const hit = document.elementFromPoint(event.clientX, event.clientY);
  if (ghost) {
    ghost.style.visibility = "";
  }
  const slot = hit?.closest("[data-slot]");
  if (slot) {
    return { kind: "slot", slot: Number(slot.dataset.slot) };
  }
  return { kind: "tray" };
}

function endDrag() {
  window.removeEventListener("pointermove", onPointerMove);
  window.removeEventListener("pointerup", onPointerUp);
  window.removeEventListener("pointercancel", onPointerCancel);
  drag = null;
}

function onPointerUp(event) {
  if (!drag || event.pointerId !== drag.pointerId) {
    return;
  }
  const { pieceId } = drag;
  const target = dropTarget(event);
  endDrag();
  puzzle = target.kind === "slot" ? place(puzzle, pieceId, target.slot) : returnToTray(puzzle, pieceId);
  render();
  if (isSolved(puzzle)) {
    onSolved();
  }
}

function onPointerCancel(event) {
  if (!drag || event.pointerId !== drag.pointerId) {
    return;
  }
  puzzle = drag.origin;
  endDrag();
  render();
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
  puzzle = createRound();
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
boot();
