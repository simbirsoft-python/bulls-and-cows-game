"""confirmation_reg

Revision ID: 91ed7b26bd9d
Revises: 8b232393cd29
Create Date: 2019-06-17 17:09:38.428971

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
from sqlalchemy.sql import expression

revision = '91ed7b26bd9d'
down_revision = '8b232393cd29'
branch_labels = None
depends_on = None


notify_type_enum = sa.Enum('confirmation_reg', 'reset_password', name='notify_type')


def upgrade():
    op.create_table(
        'email_notify',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('id_user', sa.Integer(), nullable=True),
        sa.Column('creation_date', sa.DateTime(), nullable=True),
        sa.Column('token', sa.Unicode(length=100), nullable=True),
        sa.Column('type', notify_type_enum ,nullable=True),
        sa.ForeignKeyConstraint(['id_user'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('user', sa.Column('email', sa.Unicode(length=40), nullable=False))
    op.create_unique_constraint('user_email_key', 'user', ['email'])
    op.add_column(
        'user',
        sa.Column(
            'is_active', sa.Boolean(), server_default=expression.false(),
            default=False, autoincrement=False, nullable=False
        )
    )
    op.add_column('user', sa.Column('reg_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_constraint('user_email_key', 'user', type_='unique')
    op.drop_column('user', 'email')
    op.drop_column('user', 'is_active')
    op.drop_column('user', 'reg_date')
    op.drop_table('email_notify')
    notify_type_enum.drop(op.get_bind(), checkfirst=False)
