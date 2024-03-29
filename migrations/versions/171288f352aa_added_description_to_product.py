"""Added description to product

Revision ID: 171288f352aa
Revises: 7ea9fcd8728f
Create Date: 2024-01-23 14:04:15.543355

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '171288f352aa'
down_revision = '7ea9fcd8728f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.add_column(sa.Column('description', sa.String(length=255), nullable=False))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('product', schema=None) as batch_op:
        batch_op.drop_column('description')

    # ### end Alembic commands ###
