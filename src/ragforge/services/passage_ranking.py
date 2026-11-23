"""In-memory BM25 and reciprocal rank fusion for a caller-scoped passage corpus.

Build one index from all readable passages of one active corpus revision. Form
the dense ranking under the same grant and revision before calling hybrid().
Discard this index when the grant, document revisions, or allowed scope change.
This module neither resolves permissions nor calls an embedding provider.
"""

import math
import re
import unicodedata
from collections import Counter, defaultdict
from collections.abc import Iterable
from dataclasses import dataclass


_WORD = re.compile(r"[^\W_]+")
_REFERENCE = re.compile(r"[^\W_]+(?:[-./_][^\W_]+)+")
_ORTHOGRAPHY = str.maketrans({"ى": "ي", "ـ": "", "ٱ": "ا", "‑": "-", "‐": "-", "–": "-"})
_BM25_K1 = 1.2
_BM25_B = 0.75


def _terms(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold()).translate(_ORTHOGRAPHY)
    letters = []
    for char in normalized:
        if not unicodedata.category(char).startswith("M"):
            digit = unicodedata.decimal(char, None)
            letters.append(str(digit) if digit is not None else char)
    normalized = "".join(letters)
    terms = _WORD.findall(normalized)
    for ref in _REFERENCE.findall(normalized):
        if any(char.isdigit() for char in ref):
            terms.append(ref)
    return terms


@dataclass(frozen=True)
class Passage:
    passage_id: str
    document_id: str
    text: str


@dataclass(frozen=True)
class RankedPassage:
    passage: Passage
    score: float
    lexical_rank: int | None
    dense_rank: int | None


def _check_positive(value: int, name: str) -> None:
    if type(value) is not int or value < 1:
        raise ValueError(f"{name} must be a positive integer")


class ScopedPassageIndex:
    """An immutable snapshot for local evaluation and bounded document comparison."""

    def __init__(self, passages: Iterable[Passage]):
        self._passages: dict[str, Passage] = {}
        self._postings: dict[str, dict[str, int]] = defaultdict(dict)
        self._lengths: dict[str, int] = {}
        for passage in passages:
            if not passage.passage_id.strip() or not passage.document_id.strip():
                raise ValueError("passage_id and document_id must be nonblank")
            if passage.passage_id in self._passages:
                raise ValueError(f"duplicate passage_id: {passage.passage_id}")
            counts = Counter(_terms(passage.text))
            self._passages[passage.passage_id] = passage
            self._lengths[passage.passage_id] = sum(counts.values())
            for term, count in counts.items():
                self._postings[term][passage.passage_id] = count
        self._mean_length = sum(self._lengths.values()) / max(1, len(self._passages))

    def _bm25(self, terms: list[str]) -> list[tuple[str, float]]:
        scores: dict[str, float] = defaultdict(float)
        for term in sorted(set(terms)):
            postings = self._postings.get(term)
            if not postings:
                continue
            idf = math.log1p((len(self._passages) - len(postings) + 0.5) / (len(postings) + 0.5))
            for passage_id, frequency in postings.items():
                relative_length = self._lengths[passage_id] / self._mean_length
                normalization = _BM25_K1 * (1 - _BM25_B + _BM25_B * relative_length)
                term_score = frequency * (_BM25_K1 + 1) / (frequency + normalization)
                scores[passage_id] += idf * term_score
        return sorted(scores.items(), key=lambda item: (-item[1], item[0]))

    def lexical(self, query: str, *, limit: int = 10) -> tuple[RankedPassage, ...]:
        """Score exact normalized words and reference identifiers across the full corpus."""
        _check_positive(limit, "limit")
        candidates = self._bm25(_terms(query))
        return tuple(
            RankedPassage(self._passages[passage_id], score, rank, None)
            for rank, (passage_id, score) in enumerate(candidates[:limit], 1)
        )

    def hybrid(
        self,
        query: str,
        dense_ids: Iterable[str],
        *,
        limit: int = 10,
        rank_constant: int = 60,
        candidate_limit: int | None = None,
    ) -> tuple[RankedPassage, ...]:
        """Fuse lexical and supplied dense rankings. Scores express ranks, not confidence.

        candidate_limit optionally limits each input list before fusion. Unknown
        and duplicate dense IDs are discarded without consuming a rank position.
        """
        _check_positive(limit, "limit")
        _check_positive(rank_constant, "rank_constant")
        if candidate_limit is not None:
            _check_positive(candidate_limit, "candidate_limit")
        terms = _terms(query)
        if not terms:
            return ()
        lexical = {
            passage_id: rank
            for rank, (passage_id, _) in enumerate(self._bm25(terms)[:candidate_limit], 1)
        }
        dense: dict[str, int] = {}
        for passage_id in dense_ids:
            if passage_id in self._passages and passage_id not in dense:
                dense[passage_id] = len(dense) + 1
                if len(dense) == candidate_limit:
                    break
        results = []
        for passage_id in lexical.keys() | dense.keys():
            ranks = lexical.get(passage_id), dense.get(passage_id)
            score = sum(1.0 / (rank_constant + rank) for rank in ranks if rank is not None)
            results.append(RankedPassage(self._passages[passage_id], score, ranks[0], ranks[1]))
        results.sort(key=lambda hit: (-hit.score, hit.passage.passage_id))
        return tuple(results[:limit])
