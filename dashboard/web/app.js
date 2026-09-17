import { elapsed, formatClock, idleRun, reset, start, stop } from "./clock.js";

const body = document.body;
const runnerEl = document.querySelector("#runner");
const phaseEl = document.querySelector("#phase");
const clockEl = document.querySelector("#clock");
const ranksEl = document.querySelector("#ranks");
const emptyEl = document.querySelector("#empty");
const nameEl = document.querySelector("#name");
const noticeEl = document.querySelector("#notice");

let run = idleRun();
let tickId = 0;

function now() {
  return performance.now();
}

function phaseLabel(status) {
  if (status === "running") return "Live";
  if (status === "stopped") return "Held";
  return "Waiting";
}

function render() {
  const ms = elapsed(run, now());
  clockEl.textContent = formatClock(ms);
  body.dataset.state = run.status;
  runnerEl.textContent = run.name || "Waiting for next run";
  phaseEl.textContent = phaseLabel(run.status);
}

function kick() {
  cancelAnimationFrame(tickId);
  render();
  if (run.status === "running") {
    tickId = requestAnimationFrame(loop);
  }
}

function loop() {
  render();
  if (run.status === "running") {
    tickId = requestAnimationFrame(loop);
  }
}

function say(message) {
  noticeEl.textContent = message;
}

function renderRanks(entries) {
  ranksEl.replaceChildren();
  emptyEl.hidden = entries.length > 0;
  for (const [index, row] of entries.entries()) {
    const li = document.createElement("li");
    const place = document.createElement("span");
    place.className = "place";
    place.textContent = String(index + 1);
    const who = document.createElement("span");
    who.className = "who";
    who.textContent = row.name;
    const when = document.createElement("span");
    when.className = "when";
    when.textContent = formatClock(row.time_ms);
    li.append(place, who, when);
    ranksEl.append(li);
  }
}

async function refreshRanks() {
  const res = await fetch("/leaderboard");
  const data = await res.json();
  renderRanks(data.entries || []);
}

function onStart() {
  const name = nameEl.value.trim();
  if (!name) {
    say("Need a name");
    nameEl.focus();
    return;
  }
  say("");
  run = start({ ...run, name }, now());
  kick();
}

function onStop() {
  run = stop(run, now());
  kick();
}

function onReset() {
  run = reset({ ...run, name: nameEl.value.trim() });
  say("");
  kick();
}

async function onFinish() {
  run = stop(run, now());
  const name = nameEl.value.trim();
  const ms = Math.round(elapsed(run, now()));
  if (!name) {
    say("Need a name");
    kick();
    nameEl.focus();
    return;
  }
  if (ms <= 0) {
    say("Start the clock first");
    kick();
    return;
  }
  try {
    const res = await fetch("/finish", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, time_ms: ms }),
    });
    const data = await res.json();
    if (!data.ok) {
      say(data.error || "Could not save");
      kick();
      return;
    }
    renderRanks(data.entries || []);
    nameEl.value = "";
    run = idleRun("");
    say("");
    kick();
    nameEl.focus();
  } catch {
    say("Could not save");
    kick();
  }
}

document.querySelector("#start").addEventListener("click", onStart);
document.querySelector("#stop").addEventListener("click", onStop);
document.querySelector("#reset").addEventListener("click", onReset);
document.querySelector("#finish").addEventListener("click", onFinish);

document.querySelector("#host").addEventListener("submit", (event) => {
  event.preventDefault();
  onStart();
});

refreshRanks().catch(() => {
  say("Could not save");
});
kick();
nameEl.focus();
