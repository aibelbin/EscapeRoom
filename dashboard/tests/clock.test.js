import test from "node:test";
import assert from "node:assert/strict";
import { elapsed, formatClock, idleRun, reset, start, stop } from "../web/clock.js";

test("formatClock uses MM:SS.t", () => {
  assert.equal(formatClock(0), "00:00.0");
  assert.equal(formatClock(492340), "08:12.3");
  assert.equal(formatClock(541000), "09:01.0");
});

test("start then elapsed follows wall time", () => {
  const run = start(idleRun("Ada Lovelace"), 1000);
  assert.equal(run.status, "running");
  assert.equal(elapsed(run, 2500), 1500);
});

test("stop freezes elapsed", () => {
  let run = start(idleRun("Ada"), 1000);
  run = stop(run, 4000);
  assert.equal(run.status, "stopped");
  assert.equal(elapsed(run, 9000), 3000);
});

test("reset clears time and keeps the name", () => {
  let run = start(idleRun("Ada"), 1000);
  run = reset(run);
  assert.equal(run.status, "idle");
  assert.equal(run.name, "Ada");
  assert.equal(elapsed(run, 8000), 0);
});
