"""Add tables

Revision ID: a6f98144ea03
Revises: 
Create Date: 2024-02-03 16:55:13.181805

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a6f98144ea03'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('message',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('item_hash', sa.String(), nullable=True),
    sa.Column('item_type', sa.String(), nullable=True),
    sa.Column('time', sa.Float(), nullable=True),
    sa.Column('message_type', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('item_hash')
    )
    op.create_index(op.f('ix_message_id'), 'message', ['id'], unique=False)
    op.create_table('node',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('aleph_node_id', sa.String(), nullable=False),
    sa.Column('type', sa.Enum('CRN', 'CCN', name='nodetype'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_node_id'), 'node', ['id'], unique=False)
    op.create_index(op.f('ix_node_aleph_node_id'), 'node', ['aleph_node_id'], unique=True)
    op.create_table('subscriber',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=True),
    sa.Column('value', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscriber_id'), 'subscriber', ['id'], unique=False)
    op.create_table('ccn_metric',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('asn', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('as_name', sa.String(), nullable=True),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('txs_total', sa.Integer(), nullable=True),
    sa.Column('measured_at', sa.Float(), nullable=True),
    sa.Column('measured_at_formatted', sa.Float(), nullable=True),
    sa.Column('base_latency', sa.Float(), nullable=True),
    sa.Column('metrics_latency', sa.Float(), nullable=True),
    sa.Column('pending_messages', sa.Integer(), nullable=True),
    sa.Column('aggregate_latency', sa.Float(), nullable=True),
    sa.Column('base_latency_ipv4', sa.Float(), nullable=True),
    sa.Column('eth_height_remaining', sa.Integer(), nullable=True),
    sa.Column('file_download_latency', sa.Float(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=True),
    sa.Column('message_id', sa.UUID(), nullable=True),
    sa.Column('node_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ccn_metric_id'), 'ccn_metric', ['id'], unique=False)
    op.create_table('crn_metric',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('asn', sa.Integer(), nullable=True),
    sa.Column('url', sa.String(), nullable=True),
    sa.Column('as_name', sa.String(), nullable=True),
    sa.Column('version', sa.String(), nullable=True),
    sa.Column('measured_at', sa.Float(), nullable=True),
    sa.Column('base_latency', sa.Float(), nullable=True),
    sa.Column('base_latency_ipv4', sa.Float(), nullable=True),
    sa.Column('full_check_latency', sa.Float(), nullable=True),
    sa.Column('diagnostic_vm_latency', sa.Float(), nullable=True),
    sa.Column('status', sa.Boolean(), nullable=False),
    sa.Column('message_id', sa.UUID(), nullable=True),
    sa.Column('node_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['message_id'], ['message.id'], ),
    sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crn_metric_id'), 'crn_metric', ['id'], unique=False)
    op.create_table('session',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('session_id', sa.UUID(), nullable=True),
    sa.Column('subscriber_id', sa.UUID(), nullable=True),
    sa.Column('verification_token', sa.String(), nullable=True),
    sa.Column('is_verified', sa.Boolean(), nullable=True),
    sa.Column('verified_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['subscriber_id'], ['subscriber.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_session_id'), 'session', ['id'], unique=False)
    op.create_table('subscription',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('subscriber_id', sa.UUID(), nullable=True),
    sa.Column('node_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['subscriber_id'], ['subscriber.id'], ),
    sa.ForeignKeyConstraint(['node_id'], ['node.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_subscription_id'), 'subscription', ['id'], unique=False)
    op.create_table('notification',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('message', sa.String(length=255), nullable=True),
    sa.Column('metrics_failed', sa.JSON(), nullable=True),
    sa.Column('node_status', sa.Boolean(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('subscription_id', sa.UUID(), nullable=True),
    sa.ForeignKeyConstraint(['subscription_id'], ['subscription.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notification_id'), 'notification', ['id'], unique=False)


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_notification_id'), table_name='notification')
    op.drop_table('notification')
    op.drop_index(op.f('ix_subscription_id'), table_name='subscription')
    op.drop_table('subscription')
    op.drop_index(op.f('ix_session_id'), table_name='session')
    op.drop_table('session')
    op.drop_index(op.f('ix_crn_metric_id'), table_name='crn_metric')
    op.drop_table('crn_metric')
    op.drop_index(op.f('ix_ccn_metric_id'), table_name='ccn_metric')
    op.drop_table('ccn_metric')
    op.drop_index(op.f('ix_subscriber_id'), table_name='subscriber')
    op.drop_table('subscriber')
    op.drop_index(op.f('ix_node_node_id'), table_name='node')
    op.drop_index(op.f('ix_node_id'), table_name='node')
    op.drop_table('node')
    op.drop_index(op.f('ix_message_id'), table_name='message')
    op.drop_table('message')
    # ### end Alembic commands ###
