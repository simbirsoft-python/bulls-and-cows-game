"""add_cascade_delete

Revision ID: 4b2fb8acae60
Revises: 91ed7b26bd9d
Create Date: 2019-07-17 18:25:11.824157

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4b2fb8acae60'
down_revision = '91ed7b26bd9d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint('email_notify_id_user_fkey', 'email_notify', type_='foreignkey')
    op.create_foreign_key(None, 'email_notify', 'user', ['id_user'], ['id'], ondelete='CASCADE')
    op.drop_constraint('game_id_user_fkey', 'game', type_='foreignkey')
    op.create_foreign_key(None, 'game', 'user', ['id_user'], ['id'], ondelete='CASCADE')
    op.drop_constraint('move_id_game_fkey', 'move', type_='foreignkey')
    op.create_foreign_key(None, 'move', 'game', ['id_game'], ['id'], ondelete='CASCADE')


def downgrade():
    op.drop_constraint('move_id_game_fkey', 'move', type_='foreignkey')
    op.create_foreign_key('move_id_game_fkey', 'move', 'game', ['id_game'], ['id'])
    op.drop_constraint('game_id_user_fkey', 'game', type_='foreignkey')
    op.create_foreign_key('game_id_user_fkey', 'game', 'user', ['id_user'], ['id'])
    op.drop_constraint('email_notify_id_user_fkey', 'email_notify', type_='foreignkey')
    op.create_foreign_key('email_notify_id_user_fkey', 'email_notify', 'user', ['id_user'], ['id'])
