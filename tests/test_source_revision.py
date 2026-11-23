import hashlib

import pymupdf
import pytest
from bson import ObjectId

from src.ragforge.models.db_schemes import Asset
from src.ragforge.services.document_processing_service import DocumentProcessingService


def sha256(data):
    return hashlib.sha256(data).hexdigest()


def test_legacy_asset_anchors_unicode_quotes_in_extracted_txt(tmp_path):
    path = tmp_path / 'source.txt'
    path.write_bytes("Frais de séjour\r\nشروط السفر، للموظف\r\nTotal ٣٠٠".encode())
    asset = Asset(asset_project_id=ObjectId(), asset_name=path.name, storage_path=str(path))
    chunks = DocumentProcessingService().process_asset(asset, chunk_size=15, overlap_size=4)
    extracted = path.read_text(encoding='utf-8')
    assert len(chunks) > 1
    for chunk in chunks:
        metadata = chunk['metadata']
        assert metadata['source_revision'] == sha256(path.read_bytes())
        assert metadata['page_number'] == 1
        assert metadata['source'] == str(path)
        assert metadata['passage_sha256'] == sha256(chunk['content'].encode())
        assert extracted[metadata['char_start']:metadata['char_end']] == chunk['content']


def test_snapshot_binds_parsed_bytes_even_if_original_is_replaced(tmp_path, monkeypatch):
    original = b'Initial policy.'
    path = tmp_path / 'policy.txt'
    path.write_bytes(original)
    service = DocumentProcessingService()
    original_loader = service.load_document_content

    def replace_and_load(document_path):
        path.write_bytes(b'Updated policy.')
        assert document_path != path
        records = original_loader(document_path)
        records[0].metadata.update(source_revision='spoof', page_number=26, char_start=12,
                                   char_end=17, passage_sha256='spoof', start_index=64)
        return records

    monkeypatch.setattr(service, 'load_document_content', replace_and_load)
    chunk, = service.process_document_path(path, expected_revision=sha256(original))
    metadata = chunk['metadata']
    assert chunk['content'] == original.decode()
    assert metadata['source_revision'] == metadata['passage_sha256'] == sha256(original)
    assert (metadata['page_number'], metadata['char_start'], metadata['char_end']) == (1, 0, len(original))
    with pytest.raises(ValueError, match='uploaded revision'):
        service.process_document_path(path, expected_revision=sha256(original))


def test_pdf_page_anchors_are_one_based_and_offsets_restart(tmp_path):
    path = tmp_path / 'terms.pdf'
    with pymupdf.open() as document:
        for text in ('Policy on page one', 'Conditions on page two'):
            document.new_page().insert_text((80, 80), text)
        document.save(path)
    service = DocumentProcessingService()
    pages = service.load_document_content(path)
    chunks = service.process_document_path(path)
    assert [c['metadata']['page_number'] for c in chunks] == [1, 2]
    for page, chunk in zip(pages, chunks, strict=True):
        metadata = chunk['metadata']
        assert metadata['source_revision'] == sha256(path.read_bytes())
        assert metadata['source'] == str(path)
        assert page.page_content[metadata['char_start']:metadata['char_end']] == chunk['content']
