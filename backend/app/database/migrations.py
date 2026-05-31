from sqlalchemy import inspect, text

from app.database.db import engine


def ensure_sqlite_approval_columns() -> None:
    if not engine.url.drivername.startswith("sqlite"):
        return

    inspector = inspect(engine)
    if "approvals" not in inspector.get_table_names():
        return

    existing_columns = {column["name"] for column in inspector.get_columns("approvals")}
    required_columns = {
        "decided_at": "DATETIME",
        "reviewer_name": "VARCHAR",
        "decision_comment": "TEXT",
    }

    with engine.begin() as connection:
        for column_name, column_type in required_columns.items():
            if column_name not in existing_columns:
                connection.execute(text(f"ALTER TABLE approvals ADD COLUMN {column_name} {column_type}"))

