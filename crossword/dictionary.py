from collections import defaultdict


class WordRepository:
    def __init__(self, words: list[str], size: int | None = None) -> None:
        self.size: int | None = size
        normalized = sorted(
            {
                word.strip().lower()
                for word in words
                if word.strip().isalpha()
                and (size is None or len(word.strip()) == size)
            }
        )
        self.words: list[str] = normalized
        self.words_by_length: dict[int, list[str]] = self._group_by_length(normalized)
        self.pos_index_by_length: dict[int, list[defaultdict[str, set[int]]]] = {
            length: self._build_pos_index(bucket, length)
            for length, bucket in self.words_by_length.items()
        }
        self.word_scores: dict[str, int] = {
            word: self._difficulty_score(word) for word in normalized
        }

    @classmethod
    def from_file(
        cls,
        path: str,
        size: int | None = None,
        min_len: int = 3,
        max_len: int | None = None,
    ) -> "WordRepository":
        if size is not None:
            min_len = size
            max_len = size
        words: list[str] = []
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                within_max = max_len is None or len(w) <= max_len
                if len(w) >= min_len and within_max and w.isalpha():
                    words.append(w)
        return cls(words=words)

    def _group_by_length(self, words: list[str]) -> dict[int, list[str]]:
        grouped: dict[int, list[str]] = defaultdict(list)
        for word in words:
            grouped[len(word)].append(word)
        return dict(grouped)

    def _build_pos_index(
        self, words: list[str], length: int
    ) -> list[defaultdict[str, set[int]]]:
        pos_index: list[defaultdict[str, set[int]]] = [
            defaultdict(set) for _ in range(length)
        ]
        for idx, w in enumerate(words):
            for i, ch in enumerate(w):
                pos_index[i][ch].add(idx)
        return pos_index

    def pattern_candidates(self, pattern: str) -> list[str]:
        bucket = self.words_by_length.get(len(pattern), [])
        if not bucket:
            return []

        pos_index = self.pos_index_by_length[len(pattern)]
        candidates: set[int] | None = None
        for i, ch in enumerate(pattern):
            if ch == ".":
                continue
            matched: set[int] = pos_index[i].get(ch, set())
            candidates = matched if candidates is None else (candidates & matched)
            if not candidates:
                return []
        if candidates is None:
            return list(bucket)
        return [bucket[i] for i in candidates]

    def order_candidates(
        self, candidate_words: list[str], difficulty: str = "standard"
    ) -> list[str]:
        if difficulty == "easy":
            return sorted(
                candidate_words,
                key=lambda word: (self.word_scores.get(word, 0), word),
            )
        if difficulty == "hard":
            return sorted(
                candidate_words,
                key=lambda word: (self.word_scores.get(word, 0), word),
                reverse=True,
            )
        return list(candidate_words)

    def _difficulty_score(self, word: str) -> int:
        score = 0
        rare_letter_penalty: dict[str, int] = {
            "j": 6,
            "q": 7,
            "x": 6,
            "z": 6,
            "v": 3,
            "k": 3,
            "w": 2,
            "y": 2,
        }
        common_letters: set[str] = set("etaoinshrdlucm")
        vowels: set[str] = set("aeiou")

        vowel_count = 0
        for ch in word:
            score += rare_letter_penalty.get(ch, 0)
            if ch not in common_letters:
                score += 1
            if ch in vowels:
                vowel_count += 1

        if vowel_count < 2:
            score += 3
        if vowel_count > 3:
            score += 1

        for i in range(1, len(word)):
            if word[i] == word[i - 1]:
                score += 1

        return score
