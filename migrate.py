"""Lightweight schema sync: create missing tables and add missing columns.

Base.metadata.create_all() only creates tables that do not exist yet — it
never alters existing ones, so model changes (e.g. learner_profiles.bio)
silently drift from the database and every ORM query on the new column
fails with "column ... does not exist". This script compares every model
table with the live database and adds missing columns:

    python migrate.py
"""
from sqlalchemy import inspect, text

from database import Base, engine
from models.user import User
from models.career import Career
from models.course import Course
from models.mentor import Mentor
from models.learner_profile import LearnerProfile
from models.chat_message import ChatMessage
from models.roadmap import Roadmap
from models.project import Project
from models.mentor_session import MentorSession

# Create any table that does not exist yet (same as create_table.py).
Base.metadata.create_all(bind=engine)

# Add columns that exist on a model but not yet in the database.
inspector = inspect(engine)
added = 0
with engine.begin() as conn:
    for table_name, table in Base.metadata.tables.items():
        if not inspector.has_table(table_name):
            continue  # just created above
        existing = {col["name"] for col in inspector.get_columns(table_name)}
        for column in table.columns:
            if column.name in existing:
                continue
            column_type = column.type.compile(engine.dialect)
            conn.execute(text(
                f'ALTER TABLE {table_name} '
                f'ADD COLUMN IF NOT EXISTS {column.name} {column_type}'
            ))
            print(f'  + {table_name}.{column.name} ({column_type})')
            # Backfill existing rows with the model's scalar default, if any.
            if column.default is not None and column.default.is_scalar:
                conn.execute(
                    text(f'UPDATE {table_name} SET {column.name} = :val '
                         f'WHERE {column.name} IS NULL'),
                    {"val": column.default.arg},
                )
            added += 1

print("Schema synced." if added else "Schema already up to date.")
