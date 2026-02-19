import os
import random
import json
from urllib import request, error
from abc import ABC, abstractmethod


class ClueProvider(ABC):
    @abstractmethod
    def generate_clues(self, words, direction):
        raise NotImplementedError


class OllamaClueProvider(ClueProvider):
    def __init__(self, model="llama3.2"):
        self.model = model

    def generate_clues(self, words, direction):
        host = os.getenv("OLLAMA_HOST", "http://localhost:11434").rstrip("/")
        url = f"{host}/api/generate"
        clues = []

        for word in words:
            prompt = (
                f"Create one concise crossword clue for the answer '{word}'. "
                f"Direction: {direction}. Difficulty: medium. "
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

            clue = (data.get("response") or "").strip().strip("\"'")
            if not clue:
                return None
            clues.append(clue)

        return clues


class OpenAIClueProvider(ClueProvider):
    def __init__(self, model="gpt-4.1-mini"):
        self.model = model

    def generate_clues(self, words, direction):
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return None

        try:
            from openai import OpenAI
        except ImportError:
            return None

        client = OpenAI(api_key=api_key)
        clues = []
        for word in words:
            prompt = (
                f"Create one concise crossword clue for the answer '{word}'. "
                f"Direction: {direction}. Difficulty: medium. "
                "Rules: do not include the answer or close inflections, "
                "max 10 words, return only clue text."
            )
            response = client.responses.create(
                model=self.model,
                input=prompt,
            )
            clue = response.output_text.strip()
            if not clue:
                return None
            clues.append(clue)
        return clues


class RuleBasedClueProvider(ClueProvider):
    def generate_clues(self, words, direction):
        return [self._rule_based_clue(word, direction) for word in words]

    def _rule_based_clue(self, word, direction):
        templates = [
            f"{len(word)}-letter {direction} entry.",
            f"Puzzle fill, {len(word)} letters.",
            f"Grid answer: {len(word)} letters.",
            f"Crossword entry with {len(word)} characters.",
        ]
        return random.choice(templates)


class ClueGenerator:
    def __init__(self, provider="auto", model="llama3.2"):
        self.provider = provider
        self.model = model
        self.providers = {
            "ollama": OllamaClueProvider(model=self.model),
            "openai": OpenAIClueProvider(model=self.model),
            "rule_based": RuleBasedClueProvider(),
        }

    def generate_clues(self, words, direction):
        if self.provider == "auto":
            order = ("ollama", "openai", "rule_based")
        elif self.provider in self.providers:
            order = (self.provider,)
        else:
            raise ValueError(
                f"Unknown provider '{self.provider}'. "
                "Expected one of: auto, ollama, openai, rule_based."
            )

        for name in order:
            clues = self.providers[name].generate_clues(words, direction)
            if clues is not None:
                return clues

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
            raise RuntimeError(
                "Rule-based clue generation failed unexpectedly."
            )
        return self.providers["rule_based"].generate_clues(words, direction)
