"""Se agrego creo la clase HistorialCancion

Revision ID: 1e74e8055ca2
Revises: 0b6d16e777ff
Create Date: 2020-06-17 00:04:58.703687

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '1e74e8055ca2'
down_revision = '0b6d16e777ff'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historial_cancion',
    sa.Column('id_usuario', sa.Integer(), nullable=False),
    sa.Column('id_cancion', sa.Integer(), nullable=False),
    sa.Column('fecha_de_reproduccion', sa.Date(), nullable=False),
    sa.ForeignKeyConstraint(['id_cancion'], ['cancion.id_cancion'], ),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], ),
    sa.PrimaryKeyConstraint('id_usuario', 'id_cancion')
    )
    op.drop_table('historial_usuario_canciones')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('historial_usuario_canciones',
    sa.Column('id_usuario', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('id_cancion', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['id_cancion'], ['cancion.id_cancion'], name='historial_usuario_canciones_id_cancion_fkey'),
    sa.ForeignKeyConstraint(['id_usuario'], ['usuario.id_usuario'], name='historial_usuario_canciones_id_usuario_fkey'),
    sa.PrimaryKeyConstraint('id_usuario', 'id_cancion', name='historial_usuario_canciones_pkey')
    )
    op.drop_table('historial_cancion')
    # ### end Alembic commands ###