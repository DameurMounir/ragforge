import logging
from http import HTTPStatus

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


# Use the same logger used by Uvicorn/FastAPI.
# This is better than print() because logs are easier to inspect in production.
logger = logging.getLogger('uvicorn.error')


class PipelineService(BaseService):
    """
    Orchestrates the Branch 13 data pipeline.

    This service coordinates the complete processing flow:

    Project
        ↓
    Asset or list of assets
        ↓
    DocumentProcessingService
        ↓
    DataChunk creation
        ↓
    ChunkStore persistence
        ↓
    Asset status update
        ↓
    Pipeline report

    The route should stay thin.
    The business orchestration belongs here.
    """

    def __init__(self):
        """
        Initialize the pipeline service.

        DocumentProcessingService is used to:
        - locate the physical file,
        - load the document,
        - split it into chunks.
        """

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
        Process one asset or all FILE assets for a project.

        Processing modes:
        1. asset_id exists:
           Process one asset by MongoDB asset id.

        2. stored_filename exists:
           Process one asset by stored filename.

        3. neither asset_id nor stored_filename exists:
           Process all FILE assets attached to the project.

        Returns:
            tuple[int, dict]:
                - HTTP status code
                - JSON-ready response dictionary.
        """

        # Step 1:
        # Find the project by its public project_id.
        # Example: project13test
        project = await project_store.get_project_by_project_id(
            project_id=project_id
        )

        # If the project does not exist, stop early.
        if project is None or project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project not found.',
                'project_id': project_id,
            }

        # Step 2:
        # Resolve which asset or assets must be processed.
        #
        # This can return:
        # - one asset by asset_id,
        # - one asset by stored_filename,
        # - all FILE assets of the project.
        status_code, assets_response = await self._resolve_assets(
            project=project,
            project_id=project_id,
            process_request=process_request,
            asset_store=asset_store,
        )

        # If asset resolution failed, return the error response.
        if status_code != int(HTTPStatus.OK):
            return status_code, assets_response

        assets: list[Asset] = assets_response['assets']

        # If the project has no FILE assets, there is nothing to process.
        if not assets:
            return int(HTTPStatus.BAD_REQUEST), {
                'signal': ResponseSignal.NO_FILES_TO_PROCESS.value,
                'message': 'No FILE assets found to process.',
                'project_id': project_id,
            }

        # These lists will build the final pipeline report.
        processed_assets = []
        failed_assets = []
        skipped_assets = []

        # Global counters for the full request.
        total_inserted_chunks = 0
        total_deleted_chunks = 0

        # This flag prevents deleting project chunks multiple times.
        project_reset_done = False

        # Project-level reset is only used when processing all project assets.
        #
        # If we process all files and do_reset=True:
        #   delete all old project chunks once before the loop.
        #
        # If we process one file:
        #   delete only that asset's chunks.
        should_reset_project = (
            process_request.do_reset
            and process_request.asset_id is None
            and process_request.stored_filename is None
        )

        # Delete all old chunks for the project only once.
        if should_reset_project:
            total_deleted_chunks += (
                await chunk_store.delete_chunks_by_project_id(
                    project_id=project.id
                )
            )
            project_reset_done = True

        # Step 3:
        # Process each resolved asset.
        for asset in assets:
            # Safety check:
            # An asset without MongoDB id cannot be linked to chunks.
            if asset.id is None:
                skipped_assets.append(
                    {
                        'asset_id': None,
                        'asset_name': asset.asset_name,
                        'reason': 'Asset has no MongoDB id.',
                    }
                )
                continue

            # Branch 13 only processes FILE assets.
            # Other types like URL, AUDIO, VIDEO, IMAGE can come later.
            if asset.asset_type != AssetType.FILE:
                skipped_assets.append(
                    {
                        'asset_id': str(asset.id),
                        'asset_name': asset.asset_name,
                        'reason': 'Only FILE assets are processable now.',
                    }
                )
                continue

            # Mark the asset as currently being processed.
            await asset_store.update_asset_processing_result(
                asset_id=asset.id,
                asset_status=AssetStatus.PROCESSING.value,
                chunk_count=0,
                extraction_method='document_processing_service',
                extraction_error=None,
            )

            try:
                # Step 3.1:
                # Extract and split the physical document.
                #
                # process_asset() uses Asset.storage_path when available.
                raw_chunks = self.document_processing_service.process_asset(
                    asset=asset,
                    project_id=project_id,
                    chunk_size=process_request.chunk_size,
                    overlap_size=process_request.overlap_size,
                )

                # Step 3.2:
                # Convert raw chunks into DataChunk database objects.
                #
                # Each DataChunk must keep:
                # - chunk_project_id
                # - chunk_asset_id
                # - chunk_order
                # - chunk_text
                # - chunk_metadata
                data_chunks = self._build_data_chunks(
                    raw_chunks=raw_chunks,
                    project=project,
                    asset=asset,
                )

                # If the document produced no valid text chunks,
                # mark it as failed.
                if not data_chunks:
                    raise ValueError(
                        'Document content is empty after chunk normalization.'
                    )

                # Step 3.3:
                # Delete old chunks for this asset before inserting new ones.
                #
                # But if we already deleted all project chunks at the beginning,
                # we do not need to delete per asset again.
                if not project_reset_done:
                    total_deleted_chunks += (
                        await chunk_store.delete_chunks_by_asset_id(
                            asset_id=asset.id
                        )
                    )

                # Step 3.4:
                # Insert new chunks into MongoDB.
                inserted_count = await chunk_store.insert_many_chunks(
                    chunks=data_chunks
                )

                total_inserted_chunks += inserted_count

                # Step 3.5:
                # Mark the asset as processed and store the chunk count.
                await asset_store.update_asset_processing_result(
                    asset_id=asset.id,
                    asset_status=AssetStatus.PROCESSED.value,
                    chunk_count=inserted_count,
                    extraction_method='document_processing_service',
                    extraction_error=None,
                )

                # Build the successful asset report.
                asset_result = {
                    'asset_id': str(asset.id),
                    'asset_name': asset.asset_name,
                    'file_name': asset.file_name,
                    'status': AssetStatus.PROCESSED.value,
                    'inserted_chunks': inserted_count,
                }

                # Optional:
                # Return raw chunks only when requested.
                # Default should be False because chunks can make the response huge.
                if process_request.include_chunks:
                    asset_result['chunks'] = raw_chunks

                processed_assets.append(asset_result)

            except FileNotFoundError as error:
                # The asset exists in MongoDB but the physical file is missing.
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
                # Used for unsupported file type, empty content, or validation.
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
                # Unexpected errors should be logged with full traceback.
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

        # Step 4:
        # Decide the global response signal:
        #
        # - success if at least one asset succeeded and none failed
        # - partial_success if some succeeded and some failed
        # - failed if no asset succeeded
        response_signal = self._get_pipeline_signal(
            processed_count=len(processed_assets),
            failed_count=len(failed_assets),
        )

        # Step 5:
        # Decide the HTTP status code.
        response_status_code = self._get_pipeline_status_code(
            processed_count=len(processed_assets),
            failed_count=len(failed_assets),
        )

        # Step 6:
        # Return one clean pipeline report.
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

        This method isolates the selection logic from the main pipeline method.
        """

        if project.id is None:
            return int(HTTPStatus.NOT_FOUND), {
                'signal': ResponseSignal.PROJECT_NOT_FOUND.value,
                'message': 'Project database id not found.',
                'project_id': project_id,
            }

        # Case 1:
        # User wants to process one asset by MongoDB asset_id.
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

            # Protect the project boundary:
            # The asset must belong to the selected project.
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

        # Case 2:
        # User wants to process one asset by stored_filename.
        if process_request.stored_filename:
            asset = await asset_store.get_asset_record(
                asset_project_id=project.id,
                asset_name=process_request.stored_filename,
            )

            if asset is None:
                return int(HTTPStatus.NOT_FOUND), {
                    'signal': ResponseSignal.ASSET_NOT_FOUND.value,
                    'message': 'Asset metadata not found.',
                    'project_id': project_id,
                    'stored_filename': process_request.stored_filename,
                }

            return int(HTTPStatus.OK), {
                'assets': [asset],
            }

        # Case 3:
        # No asset was specified.
        # Therefore process all FILE assets of this project.
        assets = await asset_store.get_project_assets(
            asset_project_id=project.id,
            asset_type=AssetType.FILE.value,
        )

        return int(HTTPStatus.OK), {
            'assets': assets,
        }

    def _build_data_chunks(
        self,
        raw_chunks: list[dict],
        project: Project,
        asset: Asset,
    ) -> list[DataChunk]:
        """
        Convert raw document chunks into DataChunk database objects.

        DocumentProcessingService returns chunks as dictionaries:

            {
                'chunk_index': 1,
                'content': '...',
                'metadata': {...}
            }

        DataChunk requires:

            chunk_text
            chunk_metadata
            chunk_order
            chunk_project_id
            chunk_asset_id
        """

        if project.id is None or asset.id is None:
            return []

        data_chunks: list[DataChunk] = []

        for index, chunk in enumerate(raw_chunks, start=1):
            # Support dictionary chunks.
            if isinstance(chunk, dict):
                chunk_text = (
                    chunk.get('content')
                    or chunk.get('chunk_text')
                    or chunk.get('text')
                    or chunk.get('page_content')
                    or ''
                )
                chunk_metadata = chunk.get('metadata', {})

            # Support LangChain Document-like chunks if needed later.
            else:
                chunk_text = getattr(chunk, 'page_content', '')
                chunk_metadata = getattr(chunk, 'metadata', {})

            # Ignore empty chunks.
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
        Mark one asset as failed after processing error.
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
