import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ragforge.models import ProcessingFileType
from src.ragforge.models.db_schemes import Asset
from src.ragforge.services.base_service import BaseService
from src.ragforge.services.project_service import ProjectService


class DocumentProcessingService(BaseService):
    """
    Service responsible for processing uploaded documents.

    Responsibilities:
    - locate uploaded documents
    - detect file type
    - load document content
    - split document content into chunks
    """

    def __init__(self):
        super().__init__()
        self.project_service = ProjectService()

    def get_document_path(
        self,
        project_id: str,
        stored_filename: str,
    ) -> Path:
        """
        Return the full path of an uploaded document.

        Expected structure:
        storage/uploads/{project_id}/documents/{stored_filename}
        """

        safe_stored_filename = Path(stored_filename).name

        project_documents_dir = (
            self.project_service.get_project_documents_dir(
                project_id=project_id
            )
        )

        document_path = project_documents_dir / safe_stored_filename

        if not document_path.exists():
            raise FileNotFoundError('Document not found')

        if not document_path.is_file():
            raise FileNotFoundError('Document path is not a file')

        return document_path

    def get_asset_document_path(
        self,
        asset: Asset,
        project_id: str | None = None,
    ) -> Path:
        """
        Return the physical document path from Asset metadata.

        Branch 13 prefers asset.storage_path because the asset metadata
        is now the source of truth.
        """

        if asset.storage_path:
            document_path = Path(asset.storage_path)
        elif project_id is not None:
            document_path = self.get_document_path(
                project_id=project_id,
                stored_filename=asset.asset_name,
            )
        else:
            raise FileNotFoundError('Asset storage path is missing.')

        if not document_path.exists():
            raise FileNotFoundError('Document not found')

        if not document_path.is_file():
            raise FileNotFoundError('Document path is not a file')

        return document_path

    def get_file_extension(self, document_path: Path) -> str:
        """
        Return the file extension in lowercase.
        """

        return document_path.suffix.lower()

    def get_file_loader(self, document_path: Path):
        """
        Return the correct LangChain loader based on file extension.
        """

        file_extension = self.get_file_extension(
            document_path=document_path
        )

        if file_extension == ProcessingFileType.TXT.value:
            return TextLoader(
                str(document_path),
                encoding='utf-8',
            )

        if file_extension == ProcessingFileType.PDF.value:
            return PyMuPDFLoader(
                str(document_path)
            )

        raise ValueError('Document type not supported for processing')

    def load_document_content(self, document_path: Path):
        """
        Load document content using the selected loader.
        """

        loader = self.get_file_loader(document_path=document_path)
        return loader.load()

    def split_document_content(
        self,
        document_content: list,
        chunk_size: int = 1000,
        overlap_size: int = 200,
    ):
        """
        Split loaded document content into chunks.
        """

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=overlap_size,
            length_function=len,
            add_start_index=True,
        )

        content_texts = [
            record.page_content
            for record in document_content
        ]

        content_metadata = [
            {**(record.metadata or {}), 'page_number': page_number}
            for page_number, record in enumerate(document_content, start=1)
        ]

        return text_splitter.create_documents(
            content_texts,
            metadatas=content_metadata,
        )

    def process_document(
        self,
        project_id: str,
        stored_filename: str,
        chunk_size: int = 1000,
        overlap_size: int = 200,
    ) -> list[dict]:
        """
        Process an uploaded document using project_id + stored_filename.

        This method is kept for backward compatibility.
        """

        document_path = self.get_document_path(
            project_id=project_id,
            stored_filename=stored_filename,
        )

        return self.process_document_path(
            document_path=document_path,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

    def process_asset(
        self,
        asset: Asset,
        project_id: str | None = None,
        chunk_size: int = 1000,
        overlap_size: int = 200,
    ) -> list[dict]:
        """
        Process one asset using persisted asset metadata.
        """

        document_path = self.get_asset_document_path(
            asset=asset,
            project_id=project_id,
        )

        return self.process_document_path(
            document_path=document_path,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
            expected_revision=asset.asset_metadata.get('source_revision'),
        )

    def process_document_path(
        self,
        document_path: Path,
        chunk_size: int = 1000,
        overlap_size: int = 200,
        expected_revision: str | None = None,
    ) -> list[dict]:
        """
        Process a physical document path and return JSON-ready chunks.
        """

        # Both file-based loaders must read the exact bytes whose digest is cited.
        # A private snapshot also isolates extraction from a concurrent replacement.
        digest = hashlib.sha256()
        with TemporaryDirectory() as temporary_directory:
            snapshot = Path(temporary_directory) / ('source' + document_path.suffix)
            with document_path.open('rb') as source, snapshot.open('wb') as target:
                while block := source.read(1024 * 1024):
                    target.write(block)
                    digest.update(block)
            revision = digest.hexdigest()
            if expected_revision is not None and expected_revision != revision:
                raise ValueError('Document bytes differ from the uploaded revision.')
            document_content = self.load_document_content(document_path=snapshot)
        for record in document_content:
            for key in ('source', 'file_path'):
                if key in record.metadata:
                    record.metadata[key] = str(document_path)

        chunks = self.split_document_content(
            document_content=document_content,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        result = []
        for index, chunk in enumerate(chunks, start=1):
            page_number = chunk.metadata['page_number']
            page_text = document_content[page_number - 1].page_content
            start = chunk.metadata['start_index']
            end = start + len(chunk.page_content)
            if start < 0 or page_text[start:end] != chunk.page_content:
                raise ValueError('Extracted passage cannot be located on its source page.')
            result.append({
                'chunk_index': index,
                'content': chunk.page_content,
                'metadata': {
                    **chunk.metadata,
                    'source_revision': revision,
                    'char_start': start,
                    'char_end': end,
                    'passage_sha256': hashlib.sha256(chunk.page_content.encode('utf-8')).hexdigest(),
                },
            })
        return result
