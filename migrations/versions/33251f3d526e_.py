"""empty message

Revision ID: 33251f3d526e
Revises: b5c23f2dff4a
Create Date: 2021-07-22 19:04:47.457394

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '33251f3d526e'
down_revision = 'b5c23f2dff4a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('host', sa.Column('systeminfo', sa.String(length=255), nullable=True))
    op.add_column('host', sa.Column('open_connections', sa.String(length=255), nullable=True))
    op.add_column('host', sa.Column('arp_info', sa.String(length=255), nullable=True))
    op.add_column('host', sa.Column('network_info', sa.String(length=255), nullable=True))
    op.add_column('host', sa.Column('processes', sa.String(length=255), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('host', 'processes')
    op.drop_column('host', 'network_info')
    op.drop_column('host', 'arp_info')
    op.drop_column('host', 'open_connections')
    op.drop_column('host', 'systeminfo')
    # ### end Alembic commands ###