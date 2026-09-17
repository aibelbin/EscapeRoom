# Overall Leaderboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Local guest-facing stopwatch and ranked board that saves finishes to `leaderboard.json`.

**Architecture:** Stdlib Python server in `dashboard/` on `127.0.0.1:8766` serves a single page. Timer math lives in JS. Finish POSTs name + milliseconds; the server appends JSON and returns the ranked list. Stations are untouched.

**Tech Stack:** Python 3.12 stdlib HTTP, vanilla HTML/CSS/JS, `python3.12 -m pytest`, `node --test`.

## Global Constraints

- Local only: `127.0.0.1:8766`, no network, no accounts
- Persist finishes in `dashboard/leaderboard.json`; gitignore that file
- Timer is in-page only; refresh mid-run resets the clock
- Display format `MM:SS.t`; store integer `time_ms`
- Every Finish is a new row; do not enforce unique names
- Dark forest-green kiosk; clock is the loud object; Avenir Next; no extra npm UI libraries
- Do not change pose, dribble, or selfie
- Do not commit unless the user asks

## File map

- Create: `dashboard/leaderboard.py` — load, rank, add_finish
- Create: `dashboard/main.py` — static files + GET /leaderboard + POST /finish
- Create: `dashboard/web/clock.js` — formatClock + run start/stop/reset
- Create: `dashboard/web/app.js` — page wiring
- Create: `dashboard/web/index.html`
- Create: `dashboard/web/style.css`
- Create: `dashboard/tests/test_leaderboard.py`
- Create: `dashboard/tests/clock.test.js`
- Create: `dashboard/package.json`
- Create: `dashboard/README.md`
- Modify: `.gitignore`
- Modify: `README.md`

---

### Task 1: Leaderboard JSON store

**Files:**
- Create: `dashboard/leaderboard.py`
- Test: `dashboard/tests/test_leaderboard.py`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `load(path: Path) -> dict` with `{"entries": list}`
  - `ranked(entries: list[dict]) -> list[dict]`
  - `add_finish(path: Path, *, name: str, time_ms: int, finished_at: str) -> dict`
  - `LeaderboardError` with message suitable for the UI

- [ ] **Step 1: Write the failing tests**

```python
import json
from pathlib import Path

import pytest

from leaderboard import LeaderboardError, add_finish, load, ranked


def test_load_missing_file_is_empty(tmp_path: Path):
    assert load(tmp_path / "leaderboard.json") == {"entries": []}


def test_add_finish_appends_and_ranks(tmp_path: Path):
    path = tmp_path / "leaderboard.json"
    add_finish(path, name="Jonah Reed", time_ms=541000, finished_at="2026-09-17T19:40:00")
    result = add_finish(path, name="Ada Lovelace", time_ms=492340, finished_at="2026-09-17T19:42:03")
    names = [row["name"] for row in result["entries"]]
    assert names == ["Ada Lovelace", "Jonah Reed"]
    saved = json.loads(path.read_text())
    assert saved["entries"][0]["name"] == "Jonah Reed"
    assert ranked(saved["entries"])[0]["name"] == "Ada Lovelace"


def test_rank_ties_use_finished_at(tmp_path: Path):
    path = tmp_path / "leaderboard.json"
    add_finish(path, name="Later", time_ms=1000, finished_at="2026-09-17T20:00:00")
    add_finish(path, name="Earlier", time_ms=1000, finished_at="2026-09-17T19:00:00")
    names = [row["name"] for row in load(path)["entries"]]
    ranked_names = [row["name"] for row in ranked(load(path)["entries"])]
    assert names == ["Later", "Earlier"]
    assert ranked_names == ["Earlier", "Later"]


def test_reject_empty_name(tmp_path: Path):
    with pytest.raises(LeaderboardError, match="Need a name"):
        add_finish(tmp_path / "leaderboard.json", name="   ", time_ms=1000, finished_at="2026-09-17T19:00:00")


def test_reject_zero_time(tmp_path: Path):
    with pytest.raises(LeaderboardError, match="Start the clock first"):
        add_finish(tmp_path / "leaderboard.json", name="Ada", time_ms=0, finished_at="2026-09-17T19:00:00")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd dashboard && python3.12 -m pytest tests/test_leaderboard.py -v`

Expected: FAIL with `ModuleNotFoundError: No module named 'leaderboard'` or import error.

- [ ] **Step 3: Write minimal implementation**

```python
from __future__ import annotations

import json
from pathlib import Path


class LeaderboardError(ValueError):
    pass


def load(path: Path) -> dict:
    if not path.is_file():
        return {"entries": []}
    data = json.loads(path.read_text())
    entries = data.get("entries")
    if not isinstance(entries, list):
        return {"entries": []}
    return {"entries": entries}


def ranked(entries: list[dict]) -> list[dict]:
    return sorted(entries, key=lambda row: (int(row["time_ms"]), str(row["finished_at"])))


def add_finish(path: Path, *, name: str, time_ms: int, finished_at: str) -> dict:
    cleaned = name.strip()
    if not cleaned:
        raise LeaderboardError("Need a name")
    if int(time_ms) <= 0:
        raise LeaderboardError("Start the clock first")
    data = load(path)
    data["entries"].append(
        {
            "name": cleaned,
            "time_ms": int(time_ms),
            "finished_at": finished_at,
        }
    )
    path.write_text(json.dumps(data, indent=2) + "\n")
    return {"entries": ranked(data["entries"])}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd dashboard && python3.12 -m pytest tests/test_leaderboard.py -v`

Expected: PASS (5 tests)

---

### Task 2: Clock and run state

**Files:**
- Create: `dashboard/web/clock.js`
- Create: `dashboard/package.json`
- Test: `dashboard/tests/clock.test.js`

**Interfaces:**
- Consumes: nothing
- Produces:
  - `formatClock(ms: number) -> string` as `MM:SS.t`
  - `idleRun(name?: string) -> { name, status: "idle", elapsedMs: 0, startedAt: null }`
  - `start(run, now) -> run` status `"running"`
  - `stop(run, now) -> run` status `"stopped"`
  - `reset(run) -> idle run` keeping the name
  - `elapsed(run, now) -> number`

- [ ] **Step 1: Write the failing tests**

```javascript
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
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd dashboard && node --test tests/clock.test.js`

Expected: FAIL, cannot find module `../web/clock.js`

- [ ] **Step 3: Write minimal implementation**

```javascript
export function formatClock(ms) {
  const totalTenths = Math.floor(Math.max(0, ms) / 100);
  const tenths = totalTenths % 10;
  const totalSeconds = Math.floor(totalTenths / 10);
  const seconds = totalSeconds % 60;
  const minutes = Math.floor(totalSeconds / 60);
  return `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}.${tenths}`;
}

export function idleRun(name = "") {
  return { name, status: "idle", elapsedMs: 0, startedAt: null };
}

export function elapsed(run, now) {
  if (run.status === "running" && run.startedAt != null) {
    return run.elapsedMs + (now - run.startedAt);
  }
  return run.elapsedMs;
}

export function start(run, now) {
  if (run.status === "running") return run;
  return { ...run, status: "running", startedAt: now };
}

export function stop(run, now) {
  if (run.status !== "running") return { ...run, status: "stopped", startedAt: null };
  return { ...run, status: "stopped", elapsedMs: elapsed(run, now), startedAt: null };
}

export function reset(run) {
  return idleRun(run.name);
}
```

`package.json`:

```json
{
  "type": "module",
  "private": true,
  "scripts": {
    "test": "node --test tests/clock.test.js"
  }
}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd dashboard && node --test tests/clock.test.js`

Expected: PASS (4 tests)

---

### Task 3: HTTP server

**Files:**
- Create: `dashboard/main.py`
- Test: `dashboard/tests/test_server.py`

**Interfaces:**
- Consumes: `load`, `ranked`, `add_finish`, `LeaderboardError` from `leaderboard.py`
- Produces: `Handler` serving static files from `dashboard/web`, `GET /leaderboard`, `POST /finish`

- [ ] **Step 1: Write the failing tests**

Use `http.client` against `ThreadingHTTPServer` in a thread, with `LEADERBOARD_PATH` pointed at `tmp_path`.

```python
import json
import threading
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

import pytest

import main
from leaderboard import add_finish


@pytest.fixture
def server(tmp_path, monkeypatch):
    path = tmp_path / "leaderboard.json"
    monkeypatch.setattr(main, "LEADERBOARD_PATH", path)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), main.Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address[:2]
    yield host, port, path
    httpd.shutdown()
    httpd.server_close()


def test_get_leaderboard_empty(server):
    host, port, _ = server
    conn = HTTPConnection(host, port, timeout=2)
    conn.request("GET", "/leaderboard")
    res = conn.getresponse()
    body = json.loads(res.read())
    assert res.status == 200
    assert body == {"entries": []}


def test_post_finish_saves(server):
    host, port, path = server
    payload = json.dumps({"name": "Ada Lovelace", "time_ms": 492340}).encode()
    conn = HTTPConnection(host, port, timeout=2)
    conn.request("POST", "/finish", body=payload, headers={"Content-Type": "application/json"})
    res = conn.getresponse()
    body = json.loads(res.read())
    assert res.status == 200
    assert body["ok"] is True
    assert body["entries"][0]["name"] == "Ada Lovelace"
    assert path.is_file()


def test_post_finish_rejects_empty_name(server):
    host, port, _ = server
    payload = json.dumps({"name": "  ", "time_ms": 1000}).encode()
    conn = HTTPConnection(host, port, timeout=2)
    conn.request("POST", "/finish", body=payload, headers={"Content-Type": "application/json"})
    res = conn.getresponse()
    body = json.loads(res.read())
    assert res.status == 400
    assert body["ok"] is False
    assert body["error"] == "Need a name"
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `cd dashboard && python3.12 -m pytest tests/test_server.py -v`

Expected: FAIL, cannot import `main`

- [ ] **Step 3: Write `main.py`**

Mirror selfie: `MIME` map, `do_GET` for `/`, `/leaderboard`, and files under `WEB`. `do_POST` `/finish` reads JSON, calls `add_finish` with `datetime.now().isoformat(timespec="seconds")`. `LeaderboardError` → 400. Other exceptions → 500 `"Could not save"`. `main()` binds `127.0.0.1:8766`, prints the URL, opens the browser, serves until Ctrl+C.

- [ ] **Step 4: Run tests to verify they pass**

Run: `cd dashboard && python3.12 -m pytest -v`

Expected: PASS including Task 1 tests

---

### Task 4: Page UI

**Files:**
- Create: `dashboard/web/index.html`
- Create: `dashboard/web/style.css`
- Create: `dashboard/web/app.js`

**Interfaces:**
- Consumes: `clock.js`, `GET /leaderboard`, `POST /finish`
- Produces: guest-facing board

**Design read:** party kiosk scoreboard for guests waiting in a green-themed physical escape room; live race-clock language; native CSS + macOS system type (offline).

**Dials:** variance 4, motion 3, density 5. Clock is the one loud object. No SaaS cards, no cyberpunk glow, no Inter.

- [ ] **Step 1: Markup**

`index.html`: title `Escape Room`. Regions: runner name (`#runner`), clock (`#clock`, `aria-live="polite"`), ranks (`#ranks`, ordered list), host bar with `#name`, Start, Stop, Reset, Finish, `#notice` for errors. Script `type="module"` `app.js`.

- [ ] **Step 2: CSS tokens and layout**

`:root` tokens from the spec. `min-height: 100dvh`. Wide: clock column + ranks column. Host bar sticky bottom, translucent understory. Clock `clamp(4.5rem, 18vw, 11rem)`, `font-variant-numeric: tabular-nums`, tight tracking. Rank 1 uses phosphor; others mist. Buttons: instant `:active { transform: scale(0.97) }`. `@media (prefers-reduced-motion: reduce)` disable transitions. `@media (prefers-reduced-transparency: reduce)` solid host bar.

- [ ] **Step 3: Wire `app.js`**

Load ranks on boot. Start: require trimmed name, else "Need a name". Stop pauses. Reset dumps clock, keeps name. Finish: stop if running; if elapsed 0 show "Start the clock first"; POST; on ok replace ranks, `idleRun("")`, clear the field; on fail show server error. rAF tick while running unless reduced motion, then interval 100ms or update only on stop. `data-state` on `<body>` for idle/running/stopped.

- [ ] **Step 4: Manual check**

Run: `cd dashboard && python3.12 main.py`

Open `http://127.0.0.1:8766/`. Type a name, Start, Stop, Finish. Confirm JSON on disk. Restart the process and confirm the row is still there.

---

### Task 5: Docs and gitignore

**Files:**
- Create: `dashboard/README.md`
- Modify: `README.md`
- Modify: `.gitignore`

- [ ] **Step 1: Gitignore** `dashboard/leaderboard.json`
- [ ] **Step 2: Root README** — dashboard is the start/finish board, run command, note it does not read station progress files
- [ ] **Step 3: `dashboard/README.md`** — night-of steps, buttons, JSON shape
- [ ] **Step 4: Run all tests**

```bash
cd dashboard && python3.12 -m pytest -v && node --test tests/clock.test.js
```

Expected: all pass
