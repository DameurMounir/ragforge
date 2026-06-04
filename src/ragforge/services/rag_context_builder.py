from src.ragforge.schemas.answers import AnswerEvidence, AnswerSource


class RAGContextBuilder:
    """
    Builds controlled, source-numbered RAG context from ranked evidence.

    Responsibility:
    - accept semantic search results,
    - keep source identity,
    - limit context size,
    - produce source-numbered context blocks.

    This class does not call embeddings, vector databases, or LLMs.
    """

    def build_context(
        self,
        evidence_results: list[dict],
        max_context_chars: int,
    ) -> dict:
        """
        Build context, sources, and evidence objects from search results.
        """
        context_blocks: list[str] = []
        sources: list[AnswerSource] = []
        evidence: list[AnswerEvidence] = []

        used_chars = 0

        for item in evidence_results:
            text = str(item.get('text') or '').strip()

            if not text:
                continue

            metadata = item.get('metadata') or {}
            source_number = len(sources) + 1

            source = AnswerSource(
                source_number=source_number,
                rank=int(item.get('rank') or source_number),
                score=float(item.get('score') or 0),
                record_id=str(item.get('record_id') or ''),
                chunk_id=item.get('chunk_id'),
                asset_id=item.get('asset_id'),
                project_id=item.get('project_id'),
                chunk_order=item.get('chunk_order'),
                metadata=metadata,
            )

            header = (
                f'[Source {source_number}] '
                f'rank={source.rank}; '
                f'score={source.score}; '
                f'chunk_id={source.chunk_id}; '
                f'asset_id={source.asset_id}; '
                f'chunk_order={source.chunk_order}'
            )

            remaining_chars = max_context_chars - used_chars - len(header) - 2

            if remaining_chars <= 0:
                break

            if len(text) > remaining_chars:
                text = text[:remaining_chars].rstrip() + '...'

            block = f'{header}\n{text}'

            context_blocks.append(block)
            sources.append(source)
            evidence.append(
                AnswerEvidence(
                    source_number=source_number,
                    text=text,
                    score=source.score,
                    chunk_id=source.chunk_id,
                    asset_id=source.asset_id,
                    chunk_order=source.chunk_order,
                    metadata=metadata,
                )
            )

            used_chars += len(block) + 2

        return {
            'context': '\n\n'.join(context_blocks),
            'sources': sources,
            'evidence': evidence,
        }
