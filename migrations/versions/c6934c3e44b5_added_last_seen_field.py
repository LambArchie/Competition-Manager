"""added last seen field

Revision ID: c6934c3e44b5
Revises: b7b9e60e112c
Create Date: 2019-02-12 11:29:15.744637

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c6934c3e44b5'
down_revision = 'b7b9e60e112c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('last_seen', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'last_seen')
    # ### end Alembic commands ###