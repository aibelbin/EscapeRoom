# Selfie Puzzle Implementation Plan

> Execute inline. No per-task review. No commits unless asked.

**Goal:** Local 4x4 selfie sliding puzzle with webcam snap, fallback image, green clear, progress.json.

**Architecture:** `web/puzzle.js` is the rules (tested with `node --test`). `web/app.js` is camera + DOM. `main.py` serves files and writes progress.

**Tech Stack:** Python http.server, vanilla JS, HTML/CSS

## Global Constraints

- Bind 127.0.0.1:8765 only. `id` is `selfie`. 4x4, legal-move shuffle.
- Do not edit pose or dribble apps.
