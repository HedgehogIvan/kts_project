"""Add game models

Revision ID: 4e7aa3eed640
Revises: 41d73dc34bb6
Create Date: 2023-03-15 23:12:35.238584

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4e7aa3eed640'
down_revision = '41d73dc34bb6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('chats',
    sa.Column('tg_id', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('tg_id')
    )
    op.create_table('sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.Text(), nullable=False),
    sa.Column('start_game', sa.DateTime(), nullable=False),
    sa.Column('end_game', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['chat_id'], ['chats.tg_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('tg_id', sa.Text(), nullable=False),
    sa.Column('current_chat', sa.Text(), nullable=True),
    sa.Column('current_session', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['current_chat'], ['chats.tg_id'], ),
    sa.ForeignKeyConstraint(['current_session'], ['sessions.id'], ),
    sa.PrimaryKeyConstraint('tg_id')
    )
    op.create_table('rounds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('prev_round', sa.Integer(), nullable=True),
    sa.Column('next_round', sa.Integer(), nullable=True),
    sa.Column('session', sa.Integer(), nullable=False),
    sa.Column('active_player', sa.Text(), nullable=False),
    sa.ForeignKeyConstraint(['active_player'], ['users.tg_id'], ),
    sa.ForeignKeyConstraint(['next_round'], ['rounds.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['prev_round'], ['rounds.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['session'], ['sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('score',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Text(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=True),
    sa.Column('points', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['session_id'], ['sessions.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['user_id'], ['users.tg_id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('score')
    op.drop_table('rounds')
    op.drop_table('users')
    op.drop_table('sessions')
    op.drop_table('chats')
    # ### end Alembic commands ###
