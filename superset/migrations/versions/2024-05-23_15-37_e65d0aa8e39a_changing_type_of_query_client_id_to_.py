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

# revision identifiers, used by Alembic.
revision = "e65d0aa8e39a"
down_revision = "f7b6750b67e8"


def upgrade():
    # Step 1: Add the new column
    # op.add_column('tab_state', sa.Column('latest_query_id_int', sa.Integer(), nullable=True))

    # Step 2: Update new column with casted values from the old column
    op.execute("""
        UPDATE tab_state
        SET latest_query_id_int = CAST(latest_query_id AS INTEGER)
        WHERE latest_query_id IS NOT NULL AND latest_query_id != '';
    """)

    # Step 3: Drop the old foreign key constraint if it exists
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.drop_constraint(["latest_query_id"], type_="foreignkey")

    # Step 4: Drop the old column
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.drop_column("latest_query_id")

    # Step 5: Rename the new column to the original name
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.alter_column("latest_query_id_int", new_column_name="latest_query_id")

    # Step 6: Recreate the foreign key constraint
    op.create_foreign_key(
        "fk_tab_state_latest_query_id",
        "tab_state",
        "other_table",
        ["latest_query_id"],
        ["other_id"],
    )


def downgrade():
    # Step 1: Add the old column back
    op.add_column(
        "tab_state",
        sa.Column("latest_query_id_varchar", sa.VARCHAR(length=11), nullable=True),
    )

    # Step 2: Update the old column with casted values from the new column
    op.execute("""
        UPDATE tab_state
        SET latest_query_id_varchar = CAST(latest_query_id AS VARCHAR(11))
        WHERE latest_query_id IS NOT NULL;
    """)

    # Step 3: Drop the foreign key constraint
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.drop_constraint("fk_tab_state_latest_query_id", type_="foreignkey")

    # Step 4: Drop the new column
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.drop_column("latest_query_id")

    # Step 5: Rename the old column back to the original name
    with op.batch_alter_table("tab_state") as batch_op:
        batch_op.alter_column(
            "latest_query_id_varchar", new_column_name="latest_query_id"
        )

    # Step 6: Recreate the foreign key constraint
    op.create_foreign_key(
        "fk_tab_state_latest_query_id",
        "tab_state",
        "other_table",
        ["latest_query_id"],
        ["other_id"],
    )
