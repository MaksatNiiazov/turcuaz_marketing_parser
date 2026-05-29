"""market parser module

Revision ID: 20260529_0001
Revises:
Create Date: 2026-05-29
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "20260529_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "parser_sources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("base_url", sa.String(length=500), nullable=False),
        sa.Column("type", sa.String(length=30), nullable=False, server_default="html"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("code", name="uq_parser_sources_code"),
    )
    op.create_table(
        "parser_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("parser_sources.id"), nullable=False),
        sa.Column("external_id", sa.String(length=255), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=1000), nullable=False),
        sa.Column("parent_id", sa.Integer(), sa.ForeignKey("parser_categories.id"), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_id", "external_id", name="uq_parser_categories_source_external"),
    )
    op.create_table(
        "parser_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("parser_sources.id"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("total_categories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("processed_categories", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_products", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("saved_products", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_by", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "parser_run_categories",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("parser_runs.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("parser_categories.id"), nullable=False),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="pending"),
        sa.Column("products_found", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("products_saved", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_table(
        "market_products",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("parser_sources.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("parser_categories.id"), nullable=True),
        sa.Column("external_sku", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=500), nullable=False),
        sa.Column("unit", sa.String(length=80), nullable=True),
        sa.Column("image_url", sa.String(length=1000), nullable=True),
        sa.Column("product_url", sa.String(length=1000), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("source_id", "external_sku", name="uq_market_products_source_sku"),
    )
    op.create_table(
        "market_product_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("market_products.id"), nullable=False),
        sa.Column("source_id", sa.Integer(), sa.ForeignKey("parser_sources.id"), nullable=False),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("parser_categories.id"), nullable=True),
        sa.Column("run_id", sa.Integer(), sa.ForeignKey("parser_runs.id"), nullable=True),
        sa.Column("price", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("discount_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("is_available", sa.Boolean(), nullable=True),
        sa.Column("raw_data", sa.JSON(), nullable=True),
        sa.Column("collected_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "market_product_daily_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("market_products.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("min_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("avg_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("last_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("min_discount_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("max_discount_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("was_discounted", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("available_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("snapshots_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("product_id", "date", name="uq_market_product_daily_stats_product_date"),
    )
    op.create_table(
        "market_category_daily_stats",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("category_id", sa.Integer(), sa.ForeignKey("parser_categories.id"), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("products_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("avg_price", sa.Numeric(12, 2), nullable=True),
        sa.Column("avg_discount_percent", sa.Numeric(7, 2), nullable=True),
        sa.Column("discounted_products_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("available_products_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("category_id", "date", name="uq_market_category_daily_stats_category_date"),
    )
    op.create_index("ix_market_snapshots_product_collected", "market_product_snapshots", ["product_id", "collected_at"])
    op.create_index("ix_market_snapshots_category_collected", "market_product_snapshots", ["category_id", "collected_at"])
    parser_sources = sa.table(
        "parser_sources",
        sa.column("name", sa.String),
        sa.column("code", sa.String),
        sa.column("base_url", sa.String),
        sa.column("type", sa.String),
        sa.column("is_active", sa.Boolean),
    )
    op.bulk_insert(
        parser_sources,
        [
            {
                "name": "Globus Online",
                "code": "globus",
                "base_url": "https://globus-online.kg/ru-kg",
                "type": "html",
                "is_active": True,
            }
        ],
    )


def downgrade() -> None:
    op.drop_index("ix_market_snapshots_category_collected", table_name="market_product_snapshots")
    op.drop_index("ix_market_snapshots_product_collected", table_name="market_product_snapshots")
    op.drop_table("market_category_daily_stats")
    op.drop_table("market_product_daily_stats")
    op.drop_table("market_product_snapshots")
    op.drop_table("market_products")
    op.drop_table("parser_run_categories")
    op.drop_table("parser_runs")
    op.drop_table("parser_categories")
    op.drop_table("parser_sources")
