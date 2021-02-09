"""user -> email

Revision ID: 7791d225cd50
Revises: 03304cc8e614
Create Date: 2020-09-28 21:10:46.367757

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7791d225cd50'
down_revision = '03304cc8e614'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('email', sa.String(), nullable=True))
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.drop_index('ix_users_user', table_name='users')
    op.drop_column('users', 'user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('user', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.create_index('ix_users_user', 'users', ['user'], unique=True)
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_column('users', 'email')
    # ### end Alembic commands ###
