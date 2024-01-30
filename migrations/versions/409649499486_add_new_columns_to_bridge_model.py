"""Add new columns to Bridge model

Revision ID: 409649499486
Revises: 90c6269997e5
Create Date: 2024-01-30 10:49:08.723988

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '409649499486'
down_revision = '90c6269997e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bridge', schema=None) as batch_op:
        batch_op.add_column(sa.Column('longitude', sa.Numeric(precision=9, scale=6), nullable=True))
        batch_op.add_column(sa.Column('latitude', sa.Numeric(precision=9, scale=6), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('bridge', schema=None) as batch_op:
        batch_op.drop_column('latitude')
        batch_op.drop_column('longitude')

    # ### end Alembic commands ###