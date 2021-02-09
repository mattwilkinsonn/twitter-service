"""init item

Revision ID: 03304cc8e614
Revises: 56bfcf28c912
Create Date: 2020-09-28 20:50:42.195658

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '03304cc8e614'
down_revision = '56bfcf28c912'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('items',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('item', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_items_id'), 'items', ['id'], unique=False)
    op.create_index(op.f('ix_items_item'), 'items', ['item'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_items_item'), table_name='items')
    op.drop_index(op.f('ix_items_id'), table_name='items')
    op.drop_table('items')
    # ### end Alembic commands ###