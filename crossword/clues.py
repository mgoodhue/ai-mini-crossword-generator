import os
import random
import json
import re
from urllib import request, error
from abc import ABC, abstractmethod


class ClueProvider(ABC):
    @abstractmethod
    def generate_clues(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> list[str] | None:
        raise NotImplementedError


def _normalize_clue_text(clue: str) -> str:
    text = clue.strip().strip("\"'")
    # Remove common list/number prefixes models sometimes prepend.
    text = re.sub(r"^\s*(?:\d+[\.\):\-]\s*|[A-Za-z][\.\)]\s*|[-*]\s*)", "", text)
    return text.strip()


class OllamaClueProvider(ClueProvider):
    def __init__(self, model: str = "llama3.2") -> None:
        self.model: str = model

    def generate_clues(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> list[str] | None:
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        url = f"{host}/api/generate"
        clues: list[str] = []

        for word in words:
            prompt = (
                f"Create one concise crossword clue for the answer '{word}'. "
                f"Direction: {direction}. Difficulty: {difficulty}. "
                "Rules: do not include the answer or close inflections, "
                "max 10 words, return only clue text."
            )

            payload = json.dumps(
                {
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                }
            ).encode("utf-8")
            req = request.Request(
                url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )

            try:
                with request.urlopen(req, timeout=30) as resp:
                    body = resp.read()
            except (error.URLError, TimeoutError, OSError):
                return None

            try:
                data = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return None

            clue = _normalize_clue_text(data.get("response") or "")
            if not clue:
                return None
            clues.append(clue)

        return clues


class OpenAIClueProvider(ClueProvider):
    def __init__(self, model: str = "gpt-4.1-mini") -> None:
        self.model: str = model

    def generate_clues(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> list[str] | None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        client = OpenAI(api_key=api_key)
        clues: list[str] = []
        for word in words:
            prompt = (
                f"Create one concise crossword clue for the answer '{word}'. "
                f"Direction: {direction}. Difficulty: {difficulty}. "
                "Rules: do not include the answer or close inflections, "
                "max 10 words, return only clue text."
            )
            response = client.responses.create(
                model=self.model,
                input=prompt,
            )
            clue = _normalize_clue_text(response.output_text)
            if not clue:
                return None
            clues.append(clue)
        return clues


class RuleBasedClueProvider(ClueProvider):
    def generate_clues(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> list[str]:
        return [self._rule_based_clue(word, direction) for word in words]

    def _rule_based_clue(self, word: str, direction: str) -> str:
        templates = [
            f"{len(word)}-letter {direction} entry.",
            f"Puzzle fill, {len(word)} letters.",
            f"Grid answer: {len(word)} letters.",
            f"Crossword entry with {len(word)} characters.",
        ]
        return random.choice(templates)


class ClueGenerator:
    def __init__(
        self,
        provider: str = "auto",
        model: str | None = None,
        ollama_model: str = "llama3.2",
        openai_model: str = "gpt-4.1-mini",
    ) -> None:
        self.provider: str = provider

        # Backward compatibility: historical `model` value targeted Ollama.
        if model:
            if provider == "openai":
                openai_model = model
            else:
                ollama_model = model

        self.providers: dict[str, ClueProvider] = {
            "ollama": OllamaClueProvider(model=ollama_model),
            "openai": OpenAIClueProvider(model=openai_model),
            "rule_based": RuleBasedClueProvider(),
        }

    def generate_clues_with_provider(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> tuple[list[str], str]:
        if self.provider == "auto":
            order: tuple[str, ...] = ("ollama", "openai", "rule_based")
        elif self.provider in self.providers:
            order = (self.provider,)
        else:
            raise ValueError(
                f"Unknown provider '{self.provider}'. "
                "Expected one of: auto, ollama, openai, rule_based."
            )

        for name in order:
            clues = self.providers[name].generate_clues(
                words, direction, difficulty=difficulty
            )
            if clues is not None:
                return clues, name

        if self.provider == "ollama":
            raise RuntimeError(
                "Ollama clue generation requested but unavailable. "
                "Ensure Ollama is running and the model is pulled."
            )
        if self.provider == "openai":
            raise RuntimeError(
                "OpenAI clue generation requested but unavailable. "
                "Set OPENAI_API_KEY and install the openai package."
            )
        if self.provider == "rule_based":
            raise RuntimeError("Rule-based clue generation failed unexpectedly.")
        fallback = self.providers["rule_based"].generate_clues(
            words, direction, difficulty=difficulty
        )
        if fallback is None:
            raise RuntimeError("Rule-based clue generation failed unexpectedly.")
        return fallback, "rule_based"

    def generate_clues(
        self, words: list[str], direction: str, difficulty: str = "medium"
    ) -> list[str]:
        clues, _ = self.generate_clues_with_provider(
            words, direction, difficulty=difficulty
        )
        return clues
