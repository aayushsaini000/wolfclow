"""empty message

Revision ID: daf3a4286e21
Revises: 
Create Date: 2021-06-30 17:22:12.446932

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'daf3a4286e21'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('host',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=150), nullable=True),
    sa.Column('infection_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('guid', sa.String(length=100), nullable=True),
    sa.Column('notes', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_host_ip'), 'host', ['ip'], unique=False)
    op.create_table('loot',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('data', sa.Text(), nullable=True),
    sa.Column('guid', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('task',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('task_type', sa.String(length=50), nullable=True),
    sa.Column('command', sa.String(length=300), nullable=True),
    sa.Column('output', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('guid', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=80), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_username'), 'user', ['username'], unique=True)
    op.create_table('activity',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('ip', sa.String(length=45), nullable=True),
    sa.Column('country', sa.String(length=150), nullable=True),
    sa.Column('infection_date', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('last', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('guid', sa.String(length=100), nullable=True),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.Column('action', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_activity_ip'), 'activity', ['ip'], unique=False)
    op.create_table('event',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('time', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('activity', sa.String(length=255), nullable=True),
    sa.Column('user', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['user'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('event')
    op.drop_index(op.f('ix_activity_ip'), table_name='activity')
    op.drop_table('activity')
    op.drop_index(op.f('ix_user_username'), table_name='user')
    op.drop_table('user')
    op.drop_table('task')
    op.drop_table('loot')
    op.drop_index(op.f('ix_host_ip'), table_name='host')
    op.drop_table('host')
    # ### end Alembic commands ###
