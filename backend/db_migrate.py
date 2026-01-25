"""
Автомиграции БД (упрощённо, без Alembic):

- создаёт отсутствующие таблицы
- добавляет отсутствующие колонки в существующие таблицы

Важно:
- НЕ удаляет/НЕ переименовывает/НЕ меняет типы колонок
- для SQLite это максимально безопасный вариант (ALTER TABLE ADD COLUMN поддерживается)
"""

from __future__ import annotations

from sqlalchemy import inspect, text
from sqlalchemy.schema import CreateTable

from app.database import Base, engine


def _quote(name: str) -> str:
    return engine.dialect.identifier_preparer.quote(name)


def _column_sql(col) -> str:
    # имя + тип + NULL/NOT NULL (+ default если есть server_default)
    col_name = _quote(col.name)
    col_type = col.type.compile(dialect=engine.dialect)

    parts = [col_name, col_type]
    if not col.nullable and not col.primary_key:
        parts.append("NOT NULL")
    else:
        parts.append("NULL")

    if col.server_default is not None:
        # server_default может быть TextClause/DefaultClause; для SQLite обычно ок как есть
        default_sql = str(col.server_default.arg)
        parts.append(f"DEFAULT {default_sql}")

    return " ".join(parts)


def migrate() -> None:
    # Важно: импортируем модели, чтобы Base.metadata знал про все таблицы
    import app.models  # noqa: F401

    insp = inspect(engine)
    existing_tables = set(insp.get_table_names())

    # 1) Создать отсутствующие таблицы
    for table in Base.metadata.sorted_tables:
        if table.name in existing_tables:
            continue
        ddl = str(CreateTable(table).compile(engine))
        print(f"[db_migrate] create table: {table.name}")
        with engine.begin() as conn:
            conn.execute(text(ddl))

    # 2) Добавить отсутствующие колонки
    # Ограничение: делаем только ADD COLUMN (без изменения/удаления)
    for table in Base.metadata.sorted_tables:
        if table.name not in insp.get_table_names():
            continue

        existing_cols = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name in existing_cols:
                continue
            col_def = _column_sql(col)
            sql = f"ALTER TABLE {_quote(table.name)} ADD COLUMN {col_def}"
            print(f"[db_migrate] add column: {table.name}.{col.name}")
            with engine.begin() as conn:
                conn.execute(text(sql))


if __name__ == "__main__":
    migrate()
    print("[db_migrate] done")

