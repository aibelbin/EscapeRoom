# Escape Room

Physical party room. One laptop per obstacle. Nothing talks over the network.

| Folder | Station |
|--------|---------|
| `challenges/01-pose` | Webcam pose holds. Green screen + local `progress.json` |
| `challenges/02-dribble` | Cone-lane dribble. Out of lines = red + buzzer. Finish = green + `progress.json` |
| `challenges/03-selfie-puzzle` | Webcam selfie sliding puzzle. Fallback photo if no camera. Green + `progress.json` |
| `dashboard` | Later. Reads copied progress files into a bar |
| `shared/progress.schema.json` | Shape every station writes |
