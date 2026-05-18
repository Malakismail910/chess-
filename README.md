# chess-
A Python chess game with a tkinter GUI featuring an AI opponent powered by the Minimax algorithm with Alpha-Beta pruning. Supports castling, en passant, pawn promotion, stalemate, and insufficient material detection.
# ♟️ Chess Game

A fully playable chess game built with Python featuring a desktop GUI and an AI opponent powered by the **Minimax algorithm with Alpha-Beta pruning**.

---

## Features

- 🎮 **Player vs AI** — Play as White against the computer
- 🧠 **Minimax AI** with Alpha-Beta pruning and configurable depth
- 🟢 **Move hints** — Legal moves highlighted on click
- ♟️ **Full chess rules** supported:
  - Castling (kingside & queenside)
  - En passant
  - Pawn promotion (auto-promotes to Queen)
  - Check & Checkmate detection
  - Stalemate detection
  - Insufficient material draw
- 🎨 **Clean GUI** built with Tkinter — no external dependencies needed for the interface

---

## AI Details

The AI uses the **Minimax algorithm with Alpha-Beta pruning** and evaluates positions based on:
- Material count (piece values)
- Center control bonus
- Piece mobility
- King safety
- Check detection

AI depth is configurable via `ai_level` (default: 1, higher = stronger but slower).

---

## Requirements

```
pip install chess
```

> Python 3.x and Tkinter (included with Python by default).

---

## Run

```bash
python chess.py
```

---

## Controls

| Action | How |
|--------|-----|
| Select piece | Click on it |
| Move | Click a highlighted square |
| Reset game | 🔄 button |
| Resign | 🤝 button |

---

## Project Structure

```
chess.py       # Main game file (GUI + AI + logic)
```
