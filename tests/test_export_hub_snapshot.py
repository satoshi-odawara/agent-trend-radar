import sqlite3

import export_hub_snapshot

from agent_trend_radar import storage

SAMPLE_CHECKS = {
    "has_agent_instructions": True,
    "has_tests": True,
    "has_eval": False,
    "has_ci": True,
    "ci_workflow_count": 4,
    "has_security_policy": False,
    "agent_doc_count": 1,
    "agent_doc_char_count": 1234,
    "agent_doc_heading_count": 5,
    "agent_doc_has_code_block": True,
    "agent_doc_code_block_count": 2,
    "agent_doc_mentions_test": True,
    "agent_doc_mentions_lint": False,
    "agent_doc_mentions_security": False,
    "agent_doc_mentions_commit_convention": False,
    "agent_doc_mentions_tool_usage": True,
    "agent_doc_mentions_repo_structure": True,
    "agent_doc_mentions_boundaries": False,
    "agent_doc_mentions_pr_review": False,
    "agent_doc_mentions_release_process": False,
    "has_skills_dir": True,
    "skills_count": 2,
    "has_custom_commands": True,
    "custom_commands_count": 3,
    "has_hooks_config": False,
    "mcp_servers_count": 0,
    "agent_doc_llm_cache_key": "CLAUDE.md:abc123",
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


def test_build_snapshot_includes_llm_run_metadata_when_provided():
    metadata = {"claude_cli_version": "2.1.283", "classification_prompt_hash": "abc"}
    snapshot = export_hub_snapshot.build_snapshot(_memory_conn(), llm_run_metadata=metadata)
    assert snapshot["llm_classification"] == metadata


def test_build_snapshot_omits_llm_run_metadata_when_not_provided():
    snapshot = export_hub_snapshot.build_snapshot(_memory_conn())
    assert "llm_classification" not in snapshot


def test_build_snapshot_omits_llm_run_metadata_when_empty():
    snapshot = export_hub_snapshot.build_snapshot(_memory_conn(), llm_run_metadata={})
    assert "llm_classification" not in snapshot
