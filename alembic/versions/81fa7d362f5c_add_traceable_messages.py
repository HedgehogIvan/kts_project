"""Add traceable messages

Revision ID: 81fa7d362f5c
Revises: 46ebefd67dd4
Create Date: 2023-04-05 13:00:10.258701

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '81fa7d362f5c'
down_revision = '46ebefd67dd4'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('traceable_messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('type', sa.Text(), nullable=False),
    sa.Column('message_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('message_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('traceable_messages')
    # ### end Alembic commands ###
