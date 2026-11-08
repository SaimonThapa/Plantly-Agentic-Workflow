"""Enable pgvector without choosing an embedding model or dimension."""
from alembic import op

revision = "0001_vector"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade():
    # Keep the shared extension: future tables or other schemas may depend on it.
    pass
