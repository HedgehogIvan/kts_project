"""Add game-bot tables test 3

Revision ID: 9619a4cc1fba
Revises: 41d73dc34bb6
Create Date: 2023-04-01 22:16:46.414563

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9619a4cc1fba'
down_revision = '41d73dc34bb6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('questions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('answers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=False),
    sa.Column('reward', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('current_state', sa.Text(), nullable=False),
    sa.Column('question_id', sa.Integer(), nullable=True),
    sa.Column('used_answers', sa.ARRAY(sa.Text()), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_times',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('start_game', sa.DateTime(), nullable=True),
    sa.Column('end_game', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id')
    )
    op.create_table('players',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.BigInteger(), nullable=False),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('alive', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rounds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.BigInteger(), nullable=True),
    sa.Column('session_id', sa.Integer(), nullable=False),
    sa.Column('round_number', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['session_id'], ['game_sessions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('session_id')
    )
    op.create_table('scores',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('player_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('scores')
    op.drop_table('rounds')
    op.drop_table('players')
    op.drop_table('game_times')
    op.drop_table('game_sessions')
    op.drop_table('answers')
    op.drop_table('questions')
    # ### end Alembic commands ###
