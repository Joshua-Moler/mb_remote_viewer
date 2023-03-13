"""create tables

Revision ID: 91979b40eb38
Revises: 
Create Date: 2020-03-23 14:53:53.101322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision = "91979b40eb38"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("email", sa.String(50), nullable=False),
        sa.Column("first_name", sa.String(100)),
        sa.Column("last_name", sa.String(100)),
        sa.Column("address", sa.String(100)),
        sa.Column("hashed_password", sa.String(100), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False),
        sa.Column("is_superuser", sa.Boolean, nullable=False),
    )

    # op.create_table(
    #     "valve",
    #     sa.Column("name", sa.String(50), primary_key=True),
    #     sa.Column("is_active", sa.Boolean, nullable=False),
    #     sa.Column("is_up", sa.Boolean, nullable=False),
    #     sa.Column("state", sa.String(100)),
    #     sa.Column("last_changed", sa.String(100), server_default="system"),
    #     sa.Column("last_checked", sa.DateTime, server_default=text('now()')),
    # )

    # op.create_table(
    #     "pressure",
    #     sa.Column("name", sa.String(50), primary_key=True),
    #     sa.Column("is_active", sa.Boolean, nullable=False),
    #     sa.Column("is_up", sa.Boolean, nullable=False),
    #     sa.Column("pressure", sa.String(100)),
    #     sa.Column("last_changed", sa.String(100), server_default="system"),
    #     sa.Column("last_checked", sa.DateTime, server_default=text('now()')),
    # )

    # op.create_table(
    #     "temperature",
    #     sa.Column("name", sa.String(50), primary_key=True),
    #     sa.Column("is_active", sa.Boolean, nullable=False),
    #     sa.Column("is_up", sa.Boolean, nullable=False),
    #     sa.Column("c_temp", sa.String(100)),
    #     sa.Column("last_checked", sa.DateTime, server_default=text('now()')),
    # )

    # op.create_table(
    #     "flow",
    #     sa.Column("name", sa.String(50), primary_key=True),
    #     sa.Column("is_active", sa.Boolean, nullable=False),
    #     sa.Column("is_up", sa.Boolean, nullable=False),
    #     sa.Column("c_temp", sa.String(100)),
    #     sa.Column("last_checked", sa.DateTime, server_default=text('now()')),
    # )

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("created", sa.DateTime, server_default=text('now()')),
        sa.Column("type", sa.String(100)),
        sa.Column("user", sa.String(100), server_default="system"),
        sa.Column("name", sa.String(100)),
        sa.Column("action", sa.String(100)),
        sa.Column("description", sa.String(100))

    )


def downgrade():
    op.drop_table("user")
    op.drop_table("valve")
    # op.drop_table("flow")
    # op.drop_table("temperature")
    op.drop_table("audit_logs")
