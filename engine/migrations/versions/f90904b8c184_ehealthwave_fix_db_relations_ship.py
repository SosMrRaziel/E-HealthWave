"""EHealthWave fix db relations ship

Revision ID: f90904b8c184
Revises: 3be748765605
Create Date: 2024-09-06 21:56:19.422752

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'f90904b8c184'
down_revision = '3be748765605'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('patients', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('patients', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))

    with op.batch_alter_table('doctors', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_active', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True))

    # ### end Alembic commands ###
