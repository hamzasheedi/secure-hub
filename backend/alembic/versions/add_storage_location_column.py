"""Add storage_location column to encrypted_files table

Revision ID: 001_add_storage_location_column
Revises: 
Create Date: 2026-01-25 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column


# revision identifiers
revision = '001_add_storage_location_column'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add the storage_location column to encrypted_files table
    op.add_column('encrypted_files', sa.Column('storage_location', sa.String(), server_default='local', nullable=False))


def downgrade():
    # Remove the storage_location column from encrypted_files table
    op.drop_column('encrypted_files', 'storage_location')