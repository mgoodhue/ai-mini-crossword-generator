from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from crossword import CrosswordGenerator
from crossword.clues import ClueGenerator

BASE_DIR = Path(__file__).resolve().parent
WEB_DIR = BASE_DIR / "web"

app = FastAPI(title="Mini Crossword Generator")

# Serve static frontend assets
app.mount("/static", StaticFiles(directory=WEB_DIR / "static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/generate")
def generate(
    size: int = Query(5, ge=3, le=9),
    difficulty: str = Query("easy", pattern="^(easy|standard|hard)$"),
) -> dict:
    words_path = str(BASE_DIR / "words.txt")
    generator = CrosswordGenerator(size=size, words_path=words_path, difficulty=difficulty)
    result = generator.generate()
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="No solution found. Try a bigger/better word list.",
        )

    clue_provider = os.getenv("CLUE_PROVIDER", "auto")
    clue_generator = ClueGenerator(provider=clue_provider)
    clue_difficulty = "medium"
    if difficulty == "easy":
        clue_difficulty = "easy"
    elif difficulty == "hard":
        clue_difficulty = "hard"

    across_clues, across_provider = clue_generator.generate_clues_with_provider(
        result.across, "across", difficulty=clue_difficulty
    )
    down_clues, down_provider = clue_generator.generate_clues_with_provider(
        result.down, "down", difficulty=clue_difficulty
    )

    if across_provider == "rule_based" or down_provider == "rule_based":
        raise HTTPException(
            status_code=503,
            detail=(
                "Real clue generation is unavailable. Start Ollama with a pulled model "
                "or set OPENAI_API_KEY (and install 'openai')."
            ),
        )

    return {
        "size": size,
        "difficulty": difficulty,
        "solution": result.grid_lines,
        "across": [
            {"number": i, "clue": clue, "length": len(word)}
            for i, (word, clue) in enumerate(zip(result.across, across_clues), start=1)
        ],
        "down": [
            {"number": i, "clue": clue, "length": len(word)}
            for i, (word, clue) in enumerate(zip(result.down, down_clues), start=1)
        ],
    }
