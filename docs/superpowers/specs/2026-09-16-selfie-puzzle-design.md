# Selfie Puzzle (Challenge 03) Design

Date: 2026-09-16
Status: approved

## Problem

Third physical-room laptop. A local web page snaps a webcam selfie on Start, turns it into a 4x4 sliding puzzle, and clears when the photo is whole again. If the camera fails, a fallback image is used. Green screen plus local `progress.json`. Pose and dribble are unchanged.

## Scope

In: `challenges/03-selfie-puzzle`, stdlib Python server on 127.0.0.1:8765, 4x4 sliding tiles, camera snap with fallback, POST /complete writes shared progress schema (`id: selfie`).

Out: network, dashboard UI, accounts, changes to pose/dribble.

## Flow

Idle preview + Start. Start freezes a square mirrored crop (or fallback). Shuffle via legal moves only. Click adjacent tile to slide. Solved: green `SELFIE STATION CLEAR`, write progress once. Again reshuffles a new snap.

## Constraints

All local. Python 3.10+, Node for tests. No git commits unless asked. One review at the end.
