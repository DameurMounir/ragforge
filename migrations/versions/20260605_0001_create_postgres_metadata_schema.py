"""create postgres metadata schema

Revision ID: 20260605_0001
Revises: None
Create Date: 2026-06-05 00:01:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '20260605_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # pgcrypto provides gen_random_uuid() for server-side UUID defaults.
    op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')

    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            'project_uuid',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('project_id', sa.String(length=150), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name='pk_projects'),
        sa.UniqueConstraint('project_uuid', name='uq_projects_project_uuid'),
        sa.UniqueConstraint('project_id', name='uq_projects_project_id'),
    )

    op.create_table(
        'assets',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            'asset_uuid',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('project_pk', sa.Integer(), nullable=False),
        sa.Column('asset_type', sa.String(length=50), nullable=False),
        sa.Column('asset_name', sa.String(length=512), nullable=False),
        sa.Column('original_filename', sa.String(length=512), nullable=True),
        sa.Column('stored_filename', sa.String(length=512), nullable=True),
        sa.Column('mime_type', sa.String(length=255), nullable=True),
        sa.Column('size_bytes', sa.Integer(), nullable=True),
        sa.Column('storage_path', sa.String(length=1024), nullable=True),
        sa.Column('asset_status', sa.String(length=50), server_default=sa.text("'uploaded'"), nullable=False),
        sa.Column('chunk_count', sa.Integer(), server_default=sa.text('0'), nullable=False),
        sa.Column('extraction_method', sa.String(length=100), nullable=True),
        sa.Column('extraction_error', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['project_pk'], ['projects.id'], name='fk_assets_project_pk_projects', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_assets'),
        sa.UniqueConstraint('asset_uuid', name='uq_assets_asset_uuid'),
        sa.CheckConstraint('chunk_count >= 0', name='ck_assets_chunk_count_non_negative'),
        sa.CheckConstraint('size_bytes IS NULL OR size_bytes >= 0', name='ck_assets_size_bytes_non_negative'),
    )
    op.create_index('ix_assets_project_pk', 'assets', ['project_pk'], unique=False)
    op.create_index('ix_assets_project_type', 'assets', ['project_pk', 'asset_type'], unique=False)
    op.create_index('ix_assets_project_status', 'assets', ['project_pk', 'asset_status'], unique=False)
    op.create_index(
        'uq_assets_project_stored_filename',
        'assets',
        ['project_pk', 'stored_filename'],
        unique=True,
        postgresql_where=sa.text('stored_filename IS NOT NULL'),
    )
    op.create_index(
        'uq_assets_project_storage_path',
        'assets',
        ['project_pk', 'storage_path'],
        unique=True,
        postgresql_where=sa.text('storage_path IS NOT NULL'),
    )
    op.create_index('ix_assets_metadata_gin', 'assets', ['metadata'], unique=False, postgresql_using='gin')

    op.create_table(
        'data_chunks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column(
            'chunk_uuid',
            postgresql.UUID(as_uuid=True),
            server_default=sa.text('gen_random_uuid()'),
            nullable=False,
        ),
        sa.Column('project_pk', sa.Integer(), nullable=False),
        sa.Column('asset_pk', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('chunk_order', sa.Integer(), nullable=False),
        sa.Column('text_hash', sa.String(length=64), nullable=True),
        sa.Column('page_number', sa.Integer(), nullable=True),
        sa.Column('char_start', sa.Integer(), nullable=True),
        sa.Column('char_end', sa.Integer(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default=sa.text("'{}'::jsonb"), nullable=False),
        sa.Column('embedded', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('embedding_model', sa.String(length=255), nullable=True),
        sa.Column('indexed_in_vector_store', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('vector_record_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['asset_pk'], ['assets.id'], name='fk_data_chunks_asset_pk_assets', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['project_pk'], ['projects.id'], name='fk_data_chunks_project_pk_projects', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='pk_data_chunks'),
        sa.UniqueConstraint('chunk_uuid', name='uq_data_chunks_chunk_uuid'),
        sa.UniqueConstraint('asset_pk', 'chunk_order', name='uq_data_chunks_asset_order'),
        sa.CheckConstraint('chunk_order >= 0', name='ck_data_chunks_chunk_order_non_negative'),
        sa.CheckConstraint('page_number IS NULL OR page_number >= 0', name='ck_data_chunks_page_number_non_negative'),
        sa.CheckConstraint('char_start IS NULL OR char_start >= 0', name='ck_data_chunks_char_start_non_negative'),
        sa.CheckConstraint('char_end IS NULL OR char_end >= 0', name='ck_data_chunks_char_end_non_negative'),
        sa.CheckConstraint('char_end IS NULL OR char_start IS NULL OR char_end >= char_start', name='ck_data_chunks_valid_char_range'),
        sa.CheckConstraint("char_length(btrim(chunk_text)) > 0", name='ck_data_chunks_text_not_blank'),
        sa.CheckConstraint("embedded = false OR embedding_model IS NOT NULL", name='ck_data_chunks_embedded_requires_model'),
        sa.CheckConstraint("indexed_in_vector_store = false OR vector_record_id IS NOT NULL", name='ck_data_chunks_indexed_requires_vector_record'),
    )
    op.create_index('ix_chunks_project_pk', 'data_chunks', ['project_pk'], unique=False)
    op.create_index('ix_chunks_asset_pk', 'data_chunks', ['asset_pk'], unique=False)
    op.create_index('ix_chunks_project_asset_order', 'data_chunks', ['project_pk', 'asset_pk', 'chunk_order'], unique=False)
    op.create_index('ix_chunks_embedded', 'data_chunks', ['embedded'], unique=False)
    op.create_index('ix_chunks_vector_indexed', 'data_chunks', ['indexed_in_vector_store'], unique=False)
    op.create_index('ix_chunks_text_hash', 'data_chunks', ['text_hash'], unique=False)
    op.create_index(
        'uq_chunks_vector_record_id',
        'data_chunks',
        ['vector_record_id'],
        unique=True,
        postgresql_where=sa.text('vector_record_id IS NOT NULL'),
    )
    op.create_index('ix_chunks_metadata_gin', 'data_chunks', ['metadata'], unique=False, postgresql_using='gin')


def downgrade() -> None:
    op.drop_index('ix_chunks_metadata_gin', table_name='data_chunks')
    op.drop_index('uq_chunks_vector_record_id', table_name='data_chunks')
    op.drop_index('ix_chunks_text_hash', table_name='data_chunks')
    op.drop_index('ix_chunks_vector_indexed', table_name='data_chunks')
    op.drop_index('ix_chunks_embedded', table_name='data_chunks')
    op.drop_index('ix_chunks_project_asset_order', table_name='data_chunks')
    op.drop_index('ix_chunks_asset_pk', table_name='data_chunks')
    op.drop_index('ix_chunks_project_pk', table_name='data_chunks')
    op.drop_table('data_chunks')

    op.drop_index('ix_assets_metadata_gin', table_name='assets')
    op.drop_index('uq_assets_project_storage_path', table_name='assets')
    op.drop_index('uq_assets_project_stored_filename', table_name='assets')
    op.drop_index('ix_assets_project_status', table_name='assets')
    op.drop_index('ix_assets_project_type', table_name='assets')
    op.drop_index('ix_assets_project_pk', table_name='assets')
    op.drop_table('assets')

    op.drop_table('projects')

    # Do not drop pgcrypto automatically. Other database objects may use it.
