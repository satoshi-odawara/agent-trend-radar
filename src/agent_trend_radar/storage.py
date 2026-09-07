import os
import sqlite3
from datetime import datetime, timezone

DEFAULT_DB_PATH = "data/repo_checks.db"

# #4(ファイル存在5項目) + #5(内容分析8項目) + #15(LLM内容分析4項目)
# has_observability_depは#16で廃止(SPEC.md「廃止した項目とその理由」参照)
CHECK_COLUMNS = [
    "has_agent_instructions",
    "has_tests",
    "has_eval",
    "has_ci",
    "has_security_policy",
    "agent_doc_char_count",
    "agent_doc_heading_count",
    "agent_doc_has_code_block",
    "agent_doc_mentions_test",
    "agent_doc_mentions_lint",
    "agent_doc_mentions_security",
    "agent_doc_mentions_commit_convention",
    "agent_doc_mentions_tool_usage",
    "agent_doc_mentions_repo_structure",
    "agent_doc_mentions_boundaries",
    "agent_doc_mentions_pr_review",
    "agent_doc_mentions_release_process",
]


def connect(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    dirname = os.path.dirname(db_path)
    if dirname:
        os.makedirs(dirname, exist_ok=True)
    return sqlite3.connect(db_path)


def ensure_schema(conn: sqlite3.Connection) -> None:
    columns_sql = ",\n            ".join(f"{col} INTEGER" for col in CHECK_COLUMNS)
    conn.execute(
        f"""
        CREATE TABLE IF NOT EXISTS repo_checks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            repo TEXT NOT NULL,
            segment TEXT NOT NULL,
            monetization_model TEXT NOT NULL,
            checked_at TEXT NOT NULL,
            {columns_sql}
        )
        """
    )
    conn.commit()


def insert_repo_check(
    conn: sqlite3.Connection,
    repo: str,
    segment: str,
    monetization_model: str,
    checks: dict,
    checked_at: str | None = None,
) -> None:
    checked_at = checked_at or datetime.now(timezone.utc).isoformat()
    columns = ["repo", "segment", "monetization_model", "checked_at", *CHECK_COLUMNS]
    values = [repo, segment, monetization_model, checked_at, *(checks[col] for col in CHECK_COLUMNS)]
    placeholders = ", ".join("?" for _ in columns)
    conn.execute(
        f"INSERT INTO repo_checks ({', '.join(columns)}) VALUES ({placeholders})",
        values,
    )
    conn.commit()
