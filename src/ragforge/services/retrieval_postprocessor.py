from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievalPostprocessingConfig:
    """
    Operational controls for answer-context candidate cleanup.

    RAGForge retrieves at chunk level, then this post-processing step makes
    the evidence cleaner before prompt construction.
    """

    final_limit: int
    min_score: float | None
    max_chunks_per_asset: int
    enable_source_dedup: bool
    enable_dominant_asset: bool
    dominant_asset_score_gap: float
    dominant_asset_min_chunks: int


class RetrievalPostprocessor:
    """
    Clean semantic search candidates before answer generation.

    This service is intentionally provider-neutral. It does not know Qdrant,
    embeddings, MongoDB collections, or LLM providers.

    Responsibilities:
    - remove weak-score chunks,
    - remove duplicated chunks,
    - limit noisy over-representation from the same PDF/asset,
    - optionally prefer a dominant asset when one document clearly wins,
    - preserve multi-document evidence when scores do not show dominance.
    """

    def process(
        self,
        evidence_results: list[dict[str, Any]],
        config: RetrievalPostprocessingConfig,
    ) -> dict[str, Any]:
        """
        Return cleaned evidence and diagnostics.
        """
        diagnostics: dict[str, Any] = {
            'candidate_count': len(evidence_results),
            'removed_empty_text': 0,
            'removed_below_min_score': 0,
            'removed_duplicates': 0,
            'removed_by_asset_limit': 0,
            'dominant_asset_applied': False,
            'dominant_asset_id': None,
            'asset_distribution_before': {},
            'asset_distribution_after': {},
            'min_score': config.min_score,
            'final_limit': config.final_limit,
            'max_chunks_per_asset': config.max_chunks_per_asset,
        }

        candidates = self._normalize_candidates(evidence_results, diagnostics)
        diagnostics['asset_distribution_before'] = self._asset_distribution(
            candidates
        )

        candidates = self._filter_by_min_score(
            candidates=candidates,
            min_score=config.min_score,
            diagnostics=diagnostics,
        )

        candidates = self._deduplicate_candidates(
            candidates=candidates,
            diagnostics=diagnostics,
        )

        if config.enable_dominant_asset:
            candidates = self._apply_dominant_asset_filter(
                candidates=candidates,
                score_gap=config.dominant_asset_score_gap,
                min_chunks=config.dominant_asset_min_chunks,
                diagnostics=diagnostics,
            )

        if config.enable_source_dedup:
            candidates = self._limit_chunks_per_asset(
                candidates=candidates,
                max_chunks_per_asset=config.max_chunks_per_asset,
                diagnostics=diagnostics,
            )

        candidates = candidates[:config.final_limit]
        candidates = self._renumber_ranks(candidates)

        diagnostics['final_count'] = len(candidates)
        diagnostics['asset_distribution_after'] = self._asset_distribution(
            candidates
        )

        return {
            'results': candidates,
            'diagnostics': diagnostics,
        }

    def _normalize_candidates(
        self,
        evidence_results: list[dict[str, Any]],
        diagnostics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        candidates: list[dict[str, Any]] = []

        for item in evidence_results:
            normalized = dict(item)
            text = str(normalized.get('text') or '').strip()

            if not text:
                diagnostics['removed_empty_text'] += 1
                continue

            normalized['text'] = text
            normalized['score'] = float(normalized.get('score') or 0)
            candidates.append(normalized)

        candidates.sort(key=lambda item: item.get('score', 0), reverse=True)
        return candidates

    def _filter_by_min_score(
        self,
        candidates: list[dict[str, Any]],
        min_score: float | None,
        diagnostics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        if min_score is None:
            return candidates

        filtered = [
            item for item in candidates
            if float(item.get('score') or 0) >= min_score
        ]

        diagnostics['removed_below_min_score'] = (
            len(candidates) - len(filtered)
        )
        return filtered

    def _deduplicate_candidates(
        self,
        candidates: list[dict[str, Any]],
        diagnostics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        seen: set[tuple[Any, ...]] = set()
        unique: list[dict[str, Any]] = []

        for item in candidates:
            metadata = item.get('metadata') or {}
            key = (
                item.get('record_id'),
                item.get('chunk_id'),
                item.get('asset_id') or metadata.get('asset_id'),
                item.get('chunk_order') or metadata.get('chunk_order'),
                metadata.get('page'),
            )

            if key in seen:
                diagnostics['removed_duplicates'] += 1
                continue

            seen.add(key)
            unique.append(item)

        return unique

    def _apply_dominant_asset_filter(
        self,
        candidates: list[dict[str, Any]],
        score_gap: float,
        min_chunks: int,
        diagnostics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        grouped = self._group_by_asset(candidates)

        if len(grouped) <= 1:
            return candidates

        ranked_assets = sorted(
            grouped.items(),
            key=lambda pair: (
                max(item.get('score', 0) for item in pair[1]),
                len(pair[1]),
            ),
            reverse=True,
        )

        top_asset_id, top_items = ranked_assets[0]
        second_asset_id, second_items = ranked_assets[1]
        top_score = max(item.get('score', 0) for item in top_items)
        second_score = max(item.get('score', 0) for item in second_items)

        has_enough_chunks = len(top_items) >= min_chunks
        has_score_gap = (top_score - second_score) >= score_gap

        if has_enough_chunks and has_score_gap:
            diagnostics['dominant_asset_applied'] = True
            diagnostics['dominant_asset_id'] = top_asset_id
            diagnostics['dominant_asset_second_asset_id'] = second_asset_id
            diagnostics['dominant_asset_top_score'] = top_score
            diagnostics['dominant_asset_second_score'] = second_score
            return top_items

        return candidates

    def _limit_chunks_per_asset(
        self,
        candidates: list[dict[str, Any]],
        max_chunks_per_asset: int,
        diagnostics: dict[str, Any],
    ) -> list[dict[str, Any]]:
        if max_chunks_per_asset <= 0:
            return candidates

        kept: list[dict[str, Any]] = []
        counts: dict[str, int] = defaultdict(int)

        for item in candidates:
            asset_id = self._asset_id(item)

            if counts[asset_id] >= max_chunks_per_asset:
                diagnostics['removed_by_asset_limit'] += 1
                continue

            counts[asset_id] += 1
            kept.append(item)

        return kept

    def _group_by_asset(
        self,
        candidates: list[dict[str, Any]],
    ) -> dict[str, list[dict[str, Any]]]:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)

        for item in candidates:
            grouped[self._asset_id(item)].append(item)

        return dict(grouped)

    def _asset_distribution(
        self,
        candidates: list[dict[str, Any]],
    ) -> dict[str, int]:
        distribution: dict[str, int] = defaultdict(int)

        for item in candidates:
            distribution[self._asset_id(item)] += 1

        return dict(distribution)

    def _asset_id(self, item: dict[str, Any]) -> str:
        metadata = item.get('metadata') or {}
        return str(
            item.get('asset_id')
            or metadata.get('asset_id')
            or 'unknown_asset'
        )

    def _renumber_ranks(
        self,
        candidates: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        renumbered: list[dict[str, Any]] = []

        for rank, item in enumerate(candidates, start=1):
            updated = dict(item)
            updated['rank'] = rank
            renumbered.append(updated)

        return renumbered
