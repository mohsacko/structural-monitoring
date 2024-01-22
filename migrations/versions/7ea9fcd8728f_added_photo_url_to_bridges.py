"""Added photo_url to bridges

Revision ID: 7ea9fcd8728f
Revises: da101f0ec65a
Create Date: 2024-01-22 15:02:26.352773

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7ea9fcd8728f'
down_revision = 'da101f0ec65a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bridge', schema=None) as batch_op:
        batch_op.add_column(sa.Column('photo_url', sa.String(length=500), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bridge', schema=None) as batch_op:
        batch_op.drop_column('photo_url')

    # ### end Alembic commands ###
