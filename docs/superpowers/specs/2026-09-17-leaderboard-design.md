# Overall Leaderboard Design

Date: 2026-09-17
Status: approved

## Problem

The party needs one overall ranking for a full-room run. Stations stay isolated. A host laptop at start/finish takes a full name, runs a stopwatch, and records the finish so waiting guests can see the live clock and the board. Data must survive a laptop restart as a local JSON file.

## Scope

In: `dashboard/`, stdlib Python server on `127.0.0.1:8766`, one guest-facing page (timer + ranked list + host bar), `leaderboard.json` on disk.

Out: network, accounts, reading station `progress.json`, uniqueness enforcement, mid-run timer persistence, pose/dribble/selfie changes.

## Architecture

Same pattern as selfie: Python `ThreadingHTTPServer` serves `dashboard/web/` and writes JSON next to the app. Browser opens on launch. Timer state lives in the page. Only Finish is durable. A refresh mid-run resets the clock.

## Screen

Fullscreen dark forest-green board. Waiting guests read it from across the room.

- Top: current runner full name, or "Waiting for next run"
- Center: huge stopwatch `MM:SS.t` that ticks while running and freezes when stopped
- Side/below: ranked list (place, name, time). Fastest first. Quiet empty line when nobody has finished
- Bottom host bar: name field, Start, Stop, Reset, Finish

States: idle → running → stopped → Finish saves and returns to idle with the clock cleared. Reset from running or stopped dumps the clock without saving. Finish while running stops first, then saves.

Start requires a non-empty trimmed name. Hosts type unique full names (a number suffix if needed). Software does not reject duplicates; every Finish is a new row.

## Data

`dashboard/leaderboard.json` (gitignored):

```json
{
  "entries": [
    {
      "name": "Ada Lovelace",
      "time_ms": 492340,
      "finished_at": "2026-09-17T19:42:03"
    }
  ]
}
```

Rank by `time_ms` ascending, then `finished_at` for ties. Missing file loads as `{ "entries": [] }`.

## HTTP

- `GET /` static page
- `GET /leaderboard` → `{ "entries": [ ...ranked ] }`
- `POST /finish` JSON `{ "name": "...", "time_ms": 492340 }` → `{ "ok": true, "entries": [ ...ranked ] }` or `{ "ok": false, "error": "..." }`

`time_ms` is integer milliseconds. Display uses tenths: `MM:SS.t`.

## Errors

- Empty name on Start or Finish: inline "Need a name"
- Finish at 0 ms: "Start the clock first"
- Server write failure: "Could not save"

## Visual

Party kiosk, not a SaaS dashboard. Green is the room's forest / exit-lamp language, not a hacker terminal. The clock is the only loud object. Native CSS, macOS system type so it works offline. Dark theme locked. Press feedback on buttons. `prefers-reduced-motion` turns ticking/settling into a static update.

Tokens:

- canopy `#121c16`
- understory `#1a2a20`
- phosphor `#7ee0a0`
- phosphor-lit `#c8ffd8`
- mist `#e7f2ea`
- quiet `#8aa392`

Type: Avenir Next for names (same family as selfie). Tabular numerals on the clock. Host bar is a heavier translucent strip; ranks are unboxed rows.

## Tests

Python: load missing file, append finish, rank order, reject empty name and zero time, persist JSON.

JS: format `MM:SS.t`; start/stop/reset elapsed math.

No webcam. `python3.12 -m pytest` and `node --test`.

## Night of

```bash
cd dashboard && python3.12 main.py
```

Opens `http://127.0.0.1:8766/`. Ctrl+C stops.
