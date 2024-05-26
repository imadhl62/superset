# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
"""changing type of query.client_id to integer

Revision ID: e65d0aa8e39a
Revises: f7b6750b67e8
Create Date: 2024-05-23 15:37:37.094584

"""

import sqlalchemy as sa
from alembic import op

from superset.migrations.shared.constraints import delete_fk
from superset.migrations.shared.utils import force_add_column

# revision identifiers, used by Alembic.
revision = "e65d0aa8e39a"
down_revision = "f7b6750b67e8"


def upgrade():
    delete_fk("tab_state", {"client_id"}, "query")
    force_add_column("query", sa.Column("client_id_temp", sa.Integer(), nullable=True))

    # Object metadata for reference
    query = sa.table(
        "query",
        sa.column("client_id", sa.String),
        sa.column("client_id_temp", sa.Integer),
    )

    # update new column with casted values from the old column
    stmt = sa.update(query).values(
        client_id_temp=sa.cast(query.c.client_id, sa.Integer)
    )
    op.execute(stmt)

    # Force the right type
    force_add_column("query", sa.Column("client_id", sa.Integer(), nullable=True))

    # update new column
    stmt = sa.update(query).values(client_id=query.c.client_id_temp)
    op.execute(stmt)

    with op.batch_alter_table("query") as batch_op:
        batch_op.drop_column("client_id_temp")

    op.create_index("ix_query_client_id", "query", ["client_id"])
    # rename the new column to the original name
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.create_foreign_key(
            "fk_tab_state_latest_query_id",
            "query",
            ["latest_query_id"],
            ["client_id"],
        )


def downgrade():
    delete_fk("tab_state", {"client_id"}, "query")
    force_add_column("query", sa.Column("client_id_temp", sa.String(50), nullable=True))

    # Object metadata for reference
    query = sa.table(
        "query",
        sa.column("client_id", sa.Integer),
        sa.column("client_id_temp", sa.Integer),
    )

    # update new column with casted values from the old column
    stmt = sa.update(query).values(client_id_temp=sa.cast(query.c.client_id, sa.String))
    op.execute(stmt)

    # Force the right type
    force_add_column("query", sa.Column("client_id", sa.Integer(), nullable=True))

    # update new column
    stmt = sa.update(query).values(client_id=query.c.client_id_temp)
    op.execute(stmt)

    with op.batch_alter_table("query") as batch_op:
        batch_op.drop_column("client_id_temp")

    op.create_index("ix_query_client_id", "query", ["client_id"])

    # rename the new column to the original name
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.create_foreign_key(
            "fk_tab_state_latest_query_id",
            "query",
            ["latest_query_id"],
            ["client_id"],
        )
