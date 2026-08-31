"""add user settings"""

revision = '20260829_02'
down_revision = '20260829_01'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('users', sa.Column('notifications_enabled', sa.Boolean(), server_default=sa.true()))



def downgrade():
    op.drop_column('users', 'notifications_enabled')

