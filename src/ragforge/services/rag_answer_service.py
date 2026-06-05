from http import HTTPStatus

from src.ragforge.models.enums.response_signals import ResponseSignal
from src.ragforge.prompts.rag_answer_prompt import (
    RAG_ANSWER_SYSTEM_PROMPT,
    build_rag_answer_prompt,
)
from src.ragforge.providers.llm.schemas import LLMGenerationRequest
from src.ragforge.schemas.answers import RAGAnswerRequest
from src.ragforge.schemas.search import SemanticSearchRequest
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.citation_validator import CitationValidator
from src.ragforge.services.llm_service import LLMService
from src.ragforge.services.rag_context_builder import RAGContextBuilder
from src.ragforge.services.retrieval_postprocessor import (
    RetrievalPostprocessingConfig,
    RetrievalPostprocessor,
)
from src.ragforge.services.semantic_search_service import SemanticSearchService
from src.ragforge.stores.mongodb.project_store import ProjectStore


class RAGAnswerService(BaseService):
    """
    Grounded answer orchestration service.

    Responsibility:
    semantic search -> retrieval post-processing -> context building ->
    prompt building -> LLM generation -> citation validation.

    This service does not know:
    - vector database internals,
    - embedding provider internals,
    - concrete LLM provider internals,
    - MongoDB collection internals.
    """

    def __init__(self, settings: object):
        super().__init__()
        self.settings = settings
        self.semantic_search_service = SemanticSearchService(
            settings=settings
        )
        self.retrieval_postprocessor = RetrievalPostprocessor()
        self.context_builder = RAGContextBuilder()
        self.llm_service = LLMService(settings=settings)
        self.citation_validator = CitationValidator()

    async def answer_project_question(
        self,
        project_id: str,
        answer_request: RAGAnswerRequest,
        project_store: ProjectStore,
    ) -> tuple[int, dict]:
        """
        Generate a grounded answer for a project question.
        """
        include_sources = (
            answer_request.include_sources
            if answer_request.include_sources is not None
            else self.settings.RAG_ANSWER_INCLUDE_SOURCES_DEFAULT
        )

        include_evidence = (
            answer_request.include_evidence
            if answer_request.include_evidence is not None
            else self.settings.RAG_ANSWER_INCLUDE_EVIDENCE_DEFAULT
        )

        include_debug_prompt = (
            answer_request.include_debug_prompt
            if answer_request.include_debug_prompt is not None
            else self.settings.RAG_ANSWER_DEBUG_PROMPT_DEFAULT
        )

        final_limit = (
            answer_request.limit
            if answer_request.limit is not None
            else self.settings.RAG_ANSWER_DEFAULT_LIMIT
        )

        candidate_limit = max(
            final_limit,
            self.settings.RAG_RETRIEVAL_CANDIDATE_LIMIT,
        )
        candidate_limit = min(candidate_limit, self.settings.SEARCH_MAX_LIMIT)

        # Retrieve more candidates than the final answer needs. Filtering,
        # document grouping, deduplication, and confidence control happen in
        # RetrievalPostprocessor.
        search_request = SemanticSearchRequest(
            query=answer_request.question,
            limit=candidate_limit,
            asset_id=answer_request.asset_id,
            min_score=None,
            include_text=True,
            include_metadata=True,
        )

        search_status_code, search_response = (
            await self.semantic_search_service.search_project_chunks(
                project_id=project_id,
                search_request=search_request,
                project_store=project_store,
            )
        )

        if search_status_code != int(HTTPStatus.OK):
            return search_status_code, {
                'signal': ResponseSignal.RAG_ANSWER_FAILED.value,
                'message': 'Answer generation failed during retrieval.',
                'project_id': project_id,
                'question': answer_request.question,
                'answer': None,
                'sources': [],
                'evidence': [],
                'llm_model': None,
                'retrieval_count': 0,
                'debug_prompt': None,
                'warnings': [],
                'retrieval_diagnostics': {},
                'citation_validation': {},
                'retrieval_error': search_response,
            }

        raw_evidence_results = search_response.get('results', [])

        postprocessing_min_score = (
            answer_request.min_score
            if answer_request.min_score is not None
            else self.settings.RAG_RETRIEVAL_MIN_SCORE
        )

        postprocessed = self.retrieval_postprocessor.process(
            evidence_results=raw_evidence_results,
            config=RetrievalPostprocessingConfig(
                final_limit=final_limit,
                min_score=postprocessing_min_score,
                max_chunks_per_asset=self.settings.RAG_MAX_CHUNKS_PER_ASSET,
                enable_source_dedup=self.settings.RAG_ENABLE_SOURCE_DEDUP,
                enable_dominant_asset=(
                    self.settings.RAG_ENABLE_DOMINANT_ASSET
                    and answer_request.asset_id is None
                ),
                dominant_asset_score_gap=(
                    self.settings.RAG_DOMINANT_ASSET_SCORE_GAP
                ),
                dominant_asset_min_chunks=(
                    self.settings.RAG_DOMINANT_ASSET_MIN_CHUNKS
                ),
            ),
        )

        evidence_results = postprocessed['results']
        retrieval_diagnostics = postprocessed['diagnostics']
        warnings: list[str] = []

        if not evidence_results:
            return int(HTTPStatus.OK), {
                'signal': ResponseSignal.RAG_ANSWER_NO_CONTEXT.value,
                'message': 'No relevant indexed evidence was found.',
                'project_id': project_id,
                'question': answer_request.question,
                'answer': (
                    'I cannot generate a grounded answer because no relevant '
                    'indexed evidence was found for this project.'
                ),
                'sources': [],
                'evidence': [],
                'llm_model': None,
                'retrieval_count': 0,
                'debug_prompt': None,
                'warnings': warnings,
                'retrieval_diagnostics': retrieval_diagnostics,
                'citation_validation': {},
            }

        built_context = self.context_builder.build_context(
            evidence_results=evidence_results,
            max_context_chars=self.settings.RAG_ANSWER_MAX_CONTEXT_CHARS,
        )

        context = built_context['context']

        if not context:
            return int(HTTPStatus.OK), {
                'signal': ResponseSignal.RAG_ANSWER_NO_CONTEXT.value,
                'message': 'Retrieved evidence did not contain usable text.',
                'project_id': project_id,
                'question': answer_request.question,
                'answer': (
                    'I cannot generate a grounded answer because the retrieved '
                    'evidence did not contain usable text.'
                ),
                'sources': [],
                'evidence': [],
                'llm_model': None,
                'retrieval_count': len(evidence_results),
                'debug_prompt': None,
                'warnings': warnings,
                'retrieval_diagnostics': retrieval_diagnostics,
                'citation_validation': {},
            }

        available_source_numbers = [
            source.source_number
            for source in built_context['sources']
        ]

        prompt = build_rag_answer_prompt(
            question=answer_request.question,
            context=context,
            available_source_numbers=available_source_numbers,
        )

        try:
            llm_response = await self.llm_service.generate(
                LLMGenerationRequest(
                    provider=self.settings.LLM_PROVIDER,
                    model=self.settings.LLM_DEFAULT_MODEL,
                    prompt=prompt,
                    system_prompt=RAG_ANSWER_SYSTEM_PROMPT,
                    temperature=self.settings.LLM_TEMPERATURE,
                    max_output_tokens=self.settings.LLM_MAX_OUTPUT_TOKENS,
                )
            )
        except Exception as error:
            return int(HTTPStatus.INTERNAL_SERVER_ERROR), {
                'signal': ResponseSignal.RAG_ANSWER_FAILED.value,
                'message': 'Answer generation failed during LLM generation.',
                'project_id': project_id,
                'question': answer_request.question,
                'answer': None,
                'sources': [],
                'evidence': [],
                'llm_model': None,
                'retrieval_count': len(evidence_results),
                'debug_prompt': prompt if include_debug_prompt else None,
                'warnings': warnings,
                'retrieval_diagnostics': retrieval_diagnostics,
                'citation_validation': {},
                'error': str(error),
            }

        answer_text = llm_response.content
        citation_validation = {}

        if self.settings.RAG_ENABLE_CITATION_VALIDATION:
            citation_validation = self.citation_validator.validate_and_sanitize(
                answer=answer_text,
                valid_source_numbers=available_source_numbers,
            )
            answer_text = citation_validation['answer']

            if citation_validation['invalid_source_numbers']:
                warnings.append(
                    'The generated answer referenced invalid source numbers; '
                    'the answer was sanitized.'
                )

        sources = [
            source.model_dump()
            for source in built_context['sources']
        ] if include_sources else []

        evidence = [
            evidence_item.model_dump()
            for evidence_item in built_context['evidence']
        ] if include_evidence else []

        return int(HTTPStatus.OK), {
            'signal': ResponseSignal.RAG_ANSWER_SUCCESS.value,
            'message': 'Answer generated from retrieved evidence.',
            'project_id': project_id,
            'question': answer_request.question,
            'answer': answer_text,
            'sources': sources,
            'evidence': evidence,
            'llm_model': llm_response.model,
            'retrieval_count': len(evidence_results),
            'debug_prompt': prompt if include_debug_prompt else None,
            'warnings': warnings,
            'retrieval_diagnostics': retrieval_diagnostics,
            'citation_validation': citation_validation,
        }
