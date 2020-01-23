"""init

Revision ID: 8b232393cd29
Revises: 
Create Date: 2019-06-10 08:50:27.558208

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8b232393cd29'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nick', sa.Unicode(length=30), nullable=True),
    sa.Column('password', sa.Unicode(length=60), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_user', sa.Integer(), nullable=True),
    sa.Column('secret', sa.Unicode(length=4), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('completed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('move',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_game', sa.Integer(), nullable=True),
    sa.Column('answer', sa.Unicode(length=4), nullable=True),
    sa.ForeignKeyConstraint(['id_game'], ['game.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('move')
    op.drop_table('game')
    op.drop_table('user')
    # ### end Alembic commands ###
