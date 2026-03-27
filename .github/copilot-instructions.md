# Copilot Instructions for Jericho

Jericho is a Python library that connects learning agents with interactive
fiction (text adventure) games via a Z-machine interpreter (frotz).

## Building the Project

```bash
pip install -e '.'
```

This compiles the frotz C library and installs jericho in development mode.
Run tests with `pytest -vv tests/`.

## Game ROMs

Game ROM files (`.z3`, `.z5`, `.z8`, etc.) live in the `roms/` directory.

To download games from the canonical game suite:

```bash
# Download a specific game
curl -fsSL "https://raw.githubusercontent.com/BYU-PCCL/z-machine-games/master/jericho-game-suite/<game>.z5" -o roms/<game>.z5

# Browse the full suite at:
# https://github.com/BYU-PCCL/z-machine-games/tree/master/jericho-game-suite
```

## External Resources

### IFDB — Interactive Fiction Database

Use https://ifdb.org/ to look up game metadata, descriptions, ratings, and
details. Useful API patterns:

- Search for a game: `https://ifdb.org/search?searchfor=<game+name>`
- View a game page: `https://ifdb.org/viewgame?ifid=<IFID>`

### Transcripts — allthingsjacq.com

Game transcripts and walkthroughs are available at https://allthingsjacq.com/.
Use these to understand expected game behavior, solutions, and interaction
patterns.

### Walkthroughs (local)

The `walkthroughs/` directory contains local walkthrough files for many games.
These map game filenames to sequences of actions.
