import os
import sqlite3

from agent_trend_radar import storage

SAMPLE_CHECKS = {
    "has_agent_instructions": True,
    "has_tests": True,
    "has_eval": False,
    "has_ci": True,
    "has_security_policy": False,
    "agent_doc_char_count": 1234,
    "agent_doc_heading_count": 5,
    "agent_doc_has_code_block": True,
    "agent_doc_mentions_test": True,
    "agent_doc_mentions_lint": False,
    "agent_doc_mentions_security": False,
    "agent_doc_mentions_commit_convention": False,
    "agent_doc_mentions_tool_usage": True,
}


def _memory_conn():
    conn = sqlite3.connect(":memory:")
    storage.ensure_schema(conn)
    return conn


def test_ensure_schema_creates_repo_checks_table():
    conn = _memory_conn()
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='repo_checks'"
    )
    assert cursor.fetchone() is not None


def test_ensure_schema_is_idempotent():
    conn = _memory_conn()
    storage.ensure_schema(conn)  # 2回目でもエラーにならないこと
    cursor = conn.execute("SELECT COUNT(*) FROM repo_checks")
    assert cursor.fetchone()[0] == 0


def test_insert_repo_check_stores_all_columns():
    conn = _memory_conn()
    storage.insert_repo_check(
        conn,
        repo="owner/repo",
        segment="tool",
        monetization_model="commercial_saas",
        checks=SAMPLE_CHECKS,
        checked_at="2026-09-06T00:00:00+00:00",
    )

    row = conn.execute(
        "SELECT repo, segment, monetization_model, checked_at, "
        "has_agent_instructions, agent_doc_char_count "
        "FROM repo_checks"
    ).fetchone()

    assert row == ("owner/repo", "tool", "commercial_saas", "2026-09-06T00:00:00+00:00", 1, 1234)


def test_insert_repo_check_defaults_checked_at_when_not_given():
    conn = _memory_conn()
    storage.insert_repo_check(
        conn,
        repo="owner/repo",
        segment="tool",
        monetization_model="commercial_saas",
        checks=SAMPLE_CHECKS,
    )
    checked_at = conn.execute("SELECT checked_at FROM repo_checks").fetchone()[0]
    assert checked_at  # 何らかの値が自動で入っていること


def test_two_runs_accumulate_two_rows():
    conn = _memory_conn()
    storage.insert_repo_check(
        conn,
        repo="owner/repo",
        segment="tool",
        monetization_model="commercial_saas",
        checks=SAMPLE_CHECKS,
        checked_at="2026-09-06T00:00:00+00:00",
    )
    storage.insert_repo_check(
        conn,
        repo="owner/repo",
        segment="tool",
        monetization_model="commercial_saas",
        checks=SAMPLE_CHECKS,
        checked_at="2026-09-06T01:00:00+00:00",
    )

    count = conn.execute(
        "SELECT COUNT(*) FROM repo_checks WHERE repo = 'owner/repo'"
    ).fetchone()[0]
    assert count == 2


def test_connect_creates_parent_directory(tmp_path):
    db_path = tmp_path / "nested" / "repo_checks.db"
    assert not db_path.parent.exists()

    conn = storage.connect(str(db_path))
    storage.ensure_schema(conn)

    assert db_path.parent.exists()
    assert os.path.exists(db_path)
    conn.close()
