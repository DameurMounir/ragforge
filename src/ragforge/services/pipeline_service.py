import logging
import unicodedata
from http import HTTPStatus
from pathlib import Path as FilePath

from bson.errors import InvalidId

from src.ragforge.models import ResponseSignal
from src.ragforge.models.db_schemes import Asset, DataChunk, Project
from src.ragforge.models.enums.asset_status import AssetStatus
from src.ragforge.models.enums.asset_type import AssetType
from src.ragforge.schemas.document_processing import ProcessDocumentRequest
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.document_processing_service import (
    DocumentProcessingService,
)
from src.ragforge.stores.mongodb import AssetStore, ChunkStore, ProjectStore


logger = logging.getLogger('uvicorn.error')


class PipelineService(BaseService):
    """
    Orchestrates the Branch 13 data pipeline.

    Responsibilities:
    - resolve the target project,
    - resolve one asset or all project FILE assets,
    - call DocumentProcessingService,
    - convert raw chunks into DataChunk objects,
    - persist chunks,
    - update asset processing metadata,
    - return a clean pipeline report.
    """

    def __init__(self):
        super().__init__()
        self.document_processing_service = DocumentProcessingService()

    async def process_project_documents(
        self,
        project_id: str,
        process_request: ProcessDocumentRequest,
        project_store: ProjectStore,
        asset_store: AssetStore,
        chunk_store: ChunkStore,
    ) -> tuple[int, dict]:
        """
        Process one asset or all FILE assets for one project.
        """

        project = await project_store.get_project_by_project_id(
            project_id=project_id
        )

        if project is None or project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project not found.',
                'project_id': project_id,
            }

        status_code, assets_response = await self._resolve_assets(
            project=project,
            project_id=project_id,
            process_request=process_request,
            asset_store=asset_store,
        )

        if status_code != int(HTTPStatus.OK):
            return status_code, assets_response

        assets: list[Asset] = assets_response['assets']

        if not assets:
            return int(HTTPStatus.BAD_REQUEST), {
                'signal': ResponseSignal.NO_FILES_TO_PROCESS.value,
                'message': 'No FILE assets found to process.',
                'project_id': project_id,
            }

        processed_assets = []
        failed_assets = []
        skipped_assets = []

        total_inserted_chunks = 0
        total_deleted_chunks = 0

        project_reset_done = False

        should_reset_project = (
            process_request.do_reset
            and process_request.asset_id is None
            and process_request.stored_filename is None
        )

        if should_reset_project:
            total_deleted_chunks += (
                await chunk_store.delete_chunks_by_project_id(
                    project_id=project.id
                )
            )
            project_reset_done = True

        for asset in assets:
            if asset.id is None:
                skipped_assets.append(
                    {
                        'asset_id': None,
                        'asset_name': asset.asset_name,
                        'reason': 'Asset has no MongoDB id.',
                    }
                )
                continue

            if not self._is_file_asset(asset=asset):
                skipped_assets.append(
                    {
                        'asset_id': str(asset.id),
                        'asset_name': asset.asset_name,
                        'reason': 'Only FILE assets are processable now.',
                    }
                )
                continue

            await asset_store.update_asset_processing_result(
                asset_id=asset.id,
                asset_status=AssetStatus.PROCESSING.value,
                chunk_count=0,
                extraction_method='document_processing_service',
                extraction_error=None,
            )

            try:
                raw_chunks = self.document_processing_service.process_asset(
                    asset=asset,
                    project_id=project_id,
                    chunk_size=process_request.chunk_size,
                    overlap_size=process_request.overlap_size,
                )

                data_chunks = self._build_data_chunks(
                    raw_chunks=raw_chunks,
                    project=project,
                    asset=asset,
                )

                if not data_chunks:
                    raise ValueError(
                        'Document content is empty after chunk normalization.'
                    )

                if not project_reset_done:
                    total_deleted_chunks += (
                        await chunk_store.delete_chunks_by_asset_id(
                            asset_id=asset.id
                        )
                    )

                inserted_count = await chunk_store.insert_many_chunks(
                    chunks=data_chunks
                )

                total_inserted_chunks += inserted_count

                await asset_store.update_asset_processing_result(
                    asset_id=asset.id,
                    asset_status=AssetStatus.PROCESSED.value,
                    chunk_count=inserted_count,
                    extraction_method='document_processing_service',
                    extraction_error=None,
                )

                asset_result = {
                    'asset_id': str(asset.id),
                    'asset_name': asset.asset_name,
                    'file_name': asset.file_name,
                    'status': AssetStatus.PROCESSED.value,
                    'inserted_chunks': inserted_count,
                }

                if process_request.include_chunks:
                    asset_result['chunks'] = raw_chunks

                processed_assets.append(asset_result)

            except FileNotFoundError as error:
                logger.error(
                    f'File not found while processing asset {asset.id}: {error}'
                )

                await self._mark_asset_failed(
                    asset_store=asset_store,
                    asset=asset,
                    error=str(error),
                )

                failed_assets.append(
                    self._failed_asset_response(
                        asset=asset,
                        error=str(error),
                    )
                )

            except ValueError as error:
                logger.error(
                    f'Validation error while processing asset {asset.id}: {error}'
                )

                await self._mark_asset_failed(
                    asset_store=asset_store,
                    asset=asset,
                    error=str(error),
                )

                failed_assets.append(
                    self._failed_asset_response(
                        asset=asset,
                        error=str(error),
                    )
                )

            except Exception as error:
                logger.exception(
                    f'Unexpected error while processing asset {asset.id}: {error}'
                )

                await self._mark_asset_failed(
                    asset_store=asset_store,
                    asset=asset,
                    error=str(error),
                )

                failed_assets.append(
                    self._failed_asset_response(
                        asset=asset,
                        error=str(error),
                    )
                )

        response_signal = self._get_pipeline_signal(
            processed_count=len(processed_assets),
            failed_count=len(failed_assets),
        )

        response_status_code = self._get_pipeline_status_code(
            processed_count=len(processed_assets),
            failed_count=len(failed_assets),
        )

        return response_status_code, {
            'signal': response_signal,
            'message': 'Data pipeline processing completed.',
            'project_id': project_id,
            'mode': self._get_processing_mode(process_request),
            'chunk_size': process_request.chunk_size,
            'overlap_size': process_request.overlap_size,
            'do_reset': process_request.do_reset,
            'processed_files': len(processed_assets),
            'failed_files': len(failed_assets),
            'skipped_files': len(skipped_assets),
            'inserted_chunks': total_inserted_chunks,
            'deleted_chunks': total_deleted_chunks,
            'processed_assets': processed_assets,
            'failed_assets': failed_assets,
            'skipped_assets': skipped_assets,
        }

    async def _resolve_assets(
        self,
        project: Project,
        project_id: str,
        process_request: ProcessDocumentRequest,
        asset_store: AssetStore,
    ) -> tuple[int, dict]:
        """
        Resolve which asset or assets must be processed.

        Supported modes:
        - asset_id: process one asset by MongoDB ObjectId.
        - stored_filename: process one asset by stored filename.
        - none: process all FILE assets in the project.
        """

        if project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project database id not found.',
                'project_id': project_id,
            }

        if process_request.asset_id:
            try:
                asset = await asset_store.get_asset_by_id(
                    asset_id=process_request.asset_id
                )
            except InvalidId:
                return int(HTTPStatus.BAD_REQUEST), {
                    'signal': ResponseSignal.ASSET_NOT_FOUND.value,
                    'message': 'Invalid asset_id format.',
                    'project_id': project_id,
                    'asset_id': process_request.asset_id,
                }

            if asset is None or asset.asset_project_id != project.id:
                return int(HTTPStatus.NOT_FOUND), {
                    'signal': ResponseSignal.ASSET_NOT_FOUND.value,
                    'message': 'Asset not found in this project.',
                    'project_id': project_id,
                    'asset_id': process_request.asset_id,
                }

            return int(HTTPStatus.OK), {
                'assets': [asset],
            }

        if process_request.stored_filename:
            project_assets = await asset_store.get_project_assets(
                asset_project_id=project.id,
                asset_type=AssetType.FILE.value,
            )

            selected_asset = self._find_asset_by_filename(
                assets=project_assets,
                stored_filename=process_request.stored_filename,
            )

            if selected_asset is None:
                return int(HTTPStatus.NOT_FOUND), {
                    'signal': ResponseSignal.ASSET_NOT_FOUND.value,
                    'message': 'Asset metadata not found.',
                    'project_id': project_id,
                    'stored_filename': process_request.stored_filename,
                    'normalized_stored_filename': self._normalize_filename(
                        process_request.stored_filename
                    ),
                    'available_filenames': [
                        asset.asset_name
                        for asset in project_assets
                    ],
                    'match_debug': [
                        {
                            'asset_id': str(asset.id),
                            'asset_name': asset.asset_name,
                            'file_name': asset.file_name,
                            'candidates': self._asset_filename_candidates(
                                asset=asset
                            ),
                            'normalized_candidates': [
                                self._normalize_filename(candidate)
                                for candidate in self._asset_filename_candidates(
                                    asset=asset
                                )
                            ],
                        }
                        for asset in project_assets
                    ],
                }

            return int(HTTPStatus.OK), {
                'assets': [selected_asset],
            }

        assets = await asset_store.get_project_assets(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value,
        )

        return int(HTTPStatus.OK), {
            'assets': assets,
        }

    def _find_asset_by_filename(
        self,
        assets: list[Asset],
        stored_filename: str,
    ) -> Asset | None:
        """
        Return the first asset matching the requested stored filename.

        Matching is intentionally robust because API clients may send:
        - exact stored filename,
        - a copied filename with surrounding spaces,
        - a path ending with the stored filename,
        - a value that visually matches but differs by Unicode normalization.
        """

        requested = self._normalize_filename(stored_filename)

        for asset in assets:
            normalized_candidates = [
                self._normalize_filename(candidate)
                for candidate in self._asset_filename_candidates(asset=asset)
            ]

            if requested in normalized_candidates:
                return asset

            for candidate in normalized_candidates:
                if candidate.endswith(requested) or requested.endswith(candidate):
                    return asset

        return None

    def _normalize_filename(
        self,
        filename: str | None,
    ) -> str:
        """
        Normalize filenames before comparison.
        """

        if filename is None:
            return ''

        value = str(filename)
        value = value.strip()
        value = value.strip('"')
        value = value.strip("'")
        value = value.replace('\\', '/')
        value = FilePath(value).name
        value = unicodedata.normalize('NFKC', value)
        value = value.casefold()

        return value

    def _asset_filename_candidates(
        self,
        asset: Asset,
    ) -> list[str]:
        """
        Return all possible filename values that may identify an asset.
        """

        candidates = [
            asset.asset_name,
            asset.file_name,
        ]

        if asset.storage_path:
            candidates.append(FilePath(str(asset.storage_path)).name)

        if asset.source_uri:
            candidates.append(FilePath(str(asset.source_uri)).name)

        return [
            str(candidate)
            for candidate in candidates
            if candidate
        ]

    def _is_file_asset(
        self,
        asset: Asset,
    ) -> bool:
        """
        Return True when the asset is a FILE asset.

        asset.asset_type can be:
        - raw string: 'file'
        - enum value: AssetType.FILE
        """

        asset_type = asset.asset_type

        if isinstance(asset_type, AssetType):
            return asset_type.value == AssetType.FILE.value

        return str(asset_type) == AssetType.FILE.value

    def _build_data_chunks(
        self,
        raw_chunks: list[dict],
        project: Project,
        asset: Asset,
    ) -> list[DataChunk]:
        """
        Convert raw document chunks into DataChunk database objects.
        """

        if project.id is None or asset.id is None:
            return []

        data_chunks: list[DataChunk] = []

        for index, chunk in enumerate(raw_chunks, start=1):
            if isinstance(chunk, dict):
                chunk_text = (
                    chunk.get('content')
                    or chunk.get('chunk_text')
                    or chunk.get('text')
                    or chunk.get('page_content')
                    or ''
                )
                chunk_metadata = chunk.get('metadata', {})
            else:
                chunk_text = getattr(chunk, 'page_content', '')
                chunk_metadata = getattr(chunk, 'metadata', {})

            if not str(chunk_text).strip():
                continue

            data_chunks.append(
                DataChunk(
                    chunk_text=str(chunk_text),
                    chunk_metadata=chunk_metadata or {},
                    chunk_order=index,
                    chunk_project_id=project.id,
                    chunk_asset_id=asset.id,
                    embedded=False,
                )
            )

        return data_chunks

    async def _mark_asset_failed(
        self,
        asset_store: AssetStore,
        asset: Asset,
        error: str,
    ) -> None:
        """
        Mark one asset as failed after a processing error.
        """

        if asset.id is None:
            return

        await asset_store.update_asset_processing_result(
            asset_id=asset.id,
            asset_status=AssetStatus.FAILED.value,
            chunk_count=0,
            extraction_method='document_processing_service',
            extraction_error=error,
        )

    def _failed_asset_response(
        self,
        asset: Asset,
        error: str,
    ) -> dict:
        """
        Build the response object for one failed asset.
        """

        return {
            'asset_id': str(asset.id),
            'asset_name': asset.asset_name,
            'status': AssetStatus.FAILED.value,
            'error': error,
        }

    def _get_processing_mode(
        self,
        process_request: ProcessDocumentRequest,
    ) -> str:
        """
        Return a readable processing mode for the API response.
        """

        if process_request.asset_id:
            return 'single_asset_by_id'

        if process_request.stored_filename:
            return 'single_asset_by_filename'

        return 'all_project_file_assets'

    def _get_pipeline_signal(
        self,
        processed_count: int,
        failed_count: int,
    ) -> str:
        """
        Return the global pipeline signal.
        """

        if processed_count > 0 and failed_count > 0:
            return ResponseSignal.DOCUMENT_PROCESSING_PARTIAL_SUCCESS.value

        if processed_count > 0:
            return ResponseSignal.DOCUMENT_PROCESSING_SUCCESS.value

        return ResponseSignal.DOCUMENT_PROCESSING_FAILED.value

    def _get_pipeline_status_code(
        self,
        processed_count: int,
        failed_count: int,
    ) -> int:
        """
        Return the HTTP status code for the full pipeline result.
        """

        if processed_count > 0:
            return int(HTTPStatus.OK)

        if failed_count > 0:
            return int(HTTPStatus.INTERNAL_SERVER_ERROR)

        return int(HTTPStatus.BAD_REQUEST)
