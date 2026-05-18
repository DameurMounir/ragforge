from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.ragforge.models import ProcessingFileType
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

    def get_document_path(self, project_id: str, stored_filename: str) -> Path:
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

    def get_file_extension(self, document_path: Path) -> str:
        """
        Return the file extension in lowercase.
        """
        return document_path.suffix.lower()

    def get_file_loader(self, document_path: Path):
        """
        Return the correct LangChain loader based on file extension.
        """
        file_extension = self.get_file_extension(document_path=document_path)

        if file_extension == ProcessingFileType.TXT.value:
            return TextLoader(
                str(document_path),
                encoding='utf-8'
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
        )

        content_texts = [
            record.page_content
            for record in document_content
        ]

        content_metadata = [
            record.metadata
            for record in document_content
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
        Process an uploaded document and return JSON-ready chunks.
        """
        document_path = self.get_document_path(
            project_id=project_id,
            stored_filename=stored_filename,
        )

        document_content = self.load_document_content(
            document_path=document_path,
        )

        chunks = self.split_document_content(
            document_content=document_content,
            chunk_size=chunk_size,
            overlap_size=overlap_size,
        )

        return [
            {
                'chunk_index': index,
                'content': chunk.page_content,
                'metadata': chunk.metadata,
            }
            for index, chunk in enumerate(chunks)
        ]