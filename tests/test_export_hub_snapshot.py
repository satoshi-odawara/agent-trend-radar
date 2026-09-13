import sqlite3

import export_hub_snapshot

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
    "agent_doc_mentions_repo_structure": True,
    "agent_doc_mentions_boundaries": False,
    "agent_doc_mentions_pr_review": False,
    "agent_doc_mentions_release_process": False,
}


def _memory_conn():
    conn = sqlite3.connect(":memory:")
    storage.ensure_schema(conn)
    return conn


def test_build_snapshot_includes_generated_at():
    snapshot = export_hub_snapshot.build_snapshot(_memory_conn())
    assert "generated_at" in snapshot


def test_build_snapshot_maps_columns_to_repo_dict():
    conn = _memory_conn()
    storage.insert_repo_check(
        conn,
        repo="owner/repo",
        segment="tool",
        monetization_model="commercial_saas",
        checks=SAMPLE_CHECKS,
        checked_at="2026-09-06T00:00:00+00:00",
    )

    snapshot = export_hub_snapshot.build_snapshot(conn)

    expected = {"repo": "owner/repo", "segment": "tool", "monetization_model": "commercial_saas"}
    for col in storage.CHECK_COLUMNS:
        value = SAMPLE_CHECKS[col]
        expected[col] = int(value) if isinstance(value, bool) else value
    assert snapshot["repos"] == [expected]
