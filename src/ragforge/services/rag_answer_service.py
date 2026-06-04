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
from src.ragforge.services.llm_service import LLMService
from src.ragforge.services.rag_context_builder import RAGContextBuilder
from src.ragforge.services.semantic_search_service import SemanticSearchService
from src.ragforge.stores.mongodb.project_store import ProjectStore


class RAGAnswerService(BaseService):
    """
    Branch 18 answer orchestration service.

    Responsibility:
    semantic search -> context building -> prompt building -> LLM generation.

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
        self.context_builder = RAGContextBuilder()
        self.llm_service = LLMService(settings=settings)

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

        limit = (
            answer_request.limit
            if answer_request.limit is not None
            else self.settings.RAG_ANSWER_DEFAULT_LIMIT
        )

        search_request = SemanticSearchRequest(
            query=answer_request.question,
            limit=limit,
            asset_id=answer_request.asset_id,
            min_score=answer_request.min_score,
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
                'retrieval_error': search_response,
            }

        evidence_results = search_response.get('results', [])

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
            }

        prompt = build_rag_answer_prompt(
            question=answer_request.question,
            context=context,
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
                'error': str(error),
            }

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
            'answer': llm_response.content,
            'sources': sources,
            'evidence': evidence,
            'llm_model': llm_response.model,
            'retrieval_count': len(evidence_results),
            'debug_prompt': prompt if include_debug_prompt else None,
        }
