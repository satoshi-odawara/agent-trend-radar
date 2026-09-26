import json

import diff_snapshots as diff


def _snapshot(repos: list[dict]) -> dict:
    return {"generated_at": "2026-09-14T00:00:00+00:00", "repos": repos}


def _repo_row(repo="a/a", **overrides) -> dict:
    row = {
        "repo": repo,
        "segment": "tool",
        "monetization_model": "commercial_saas",
        "has_hooks_config": 0,
        "skills_count": 0,
        "agent_doc_mentions_boundaries": 0,
    }
    row.update(overrides)
    return row


def test_list_snapshot_dates_returns_sorted_directory_names(tmp_path):
    (tmp_path / "2026-09-14").mkdir()
    (tmp_path / "2026-09-13").mkdir()
    (tmp_path / "metrics.json").write_text("{}", encoding="utf-8")  # ディレクトリでないものは無視

    assert diff.list_snapshot_dates(str(tmp_path)) == ["2026-09-13", "2026-09-14"]


def test_list_snapshot_dates_empty_when_dir_missing(tmp_path):
    assert diff.list_snapshot_dates(str(tmp_path / "does_not_exist")) == []


def test_select_latest_two_dates_none_when_fewer_than_two():
    assert diff.select_latest_two_dates([]) is None
    assert diff.select_latest_two_dates(["2026-09-13"]) is None


def test_select_latest_two_dates_returns_two_most_recent():
    dates = ["2026-09-10", "2026-09-13", "2026-09-14"]
    assert diff.select_latest_two_dates(dates) == ("2026-09-13", "2026-09-14")


def test_diff_snapshots_detects_changed_field():
    old = _snapshot([_repo_row(has_hooks_config=0)])
    new = _snapshot([_repo_row(has_hooks_config=1)])

    changes = diff.diff_snapshots(old, new)

    assert changes == [
        {"repo": "a/a", "field": "has_hooks_config", "old_value": 0, "new_value": 1}
    ]


def test_diff_snapshots_ignores_unchanged_fields():
    old = _snapshot([_repo_row(skills_count=3)])
    new = _snapshot([_repo_row(skills_count=3)])

    assert diff.diff_snapshots(old, new) == []


def test_diff_snapshots_ignores_repos_present_in_only_one_snapshot():
    old = _snapshot([_repo_row(repo="old-only/repo", has_hooks_config=0)])
    new = _snapshot([_repo_row(repo="new-only/repo", has_hooks_config=1)])

    assert diff.diff_snapshots(old, new) == []


def test_diff_snapshots_suppresses_llm_field_when_cache_key_unchanged():
    """cache keyが同じなのにLLM分類4項目が変化している場合、#25の2bの
    非決定性による疑いとして除外する(#30の設計を活かす)。"""
    old = _repo_row(agent_doc_mentions_boundaries=0, agent_doc_llm_cache_key="CLAUDE.md:sha1")
    new = _repo_row(agent_doc_mentions_boundaries=1, agent_doc_llm_cache_key="CLAUDE.md:sha1")

    assert diff.diff_snapshots(_snapshot([old]), _snapshot([new])) == []


def test_diff_snapshots_includes_llm_field_when_cache_key_changed():
    old = _repo_row(agent_doc_mentions_boundaries=0, agent_doc_llm_cache_key="CLAUDE.md:sha1")
    new = _repo_row(agent_doc_mentions_boundaries=1, agent_doc_llm_cache_key="CLAUDE.md:sha2")

    changes = diff.diff_snapshots(_snapshot([old]), _snapshot([new]))

    assert {
        "repo": "a/a",
        "field": "agent_doc_mentions_boundaries",
        "old_value": 0,
        "new_value": 1,
    } in changes


def test_diff_snapshots_excludes_llm_field_when_cache_key_missing():
    """#30より前のスナップショット同士の比較では、cache keyが無いため
    LLM4項目は無条件で除外する(フォールバック)。"""
    old = _repo_row(agent_doc_mentions_boundaries=0)
    new = _repo_row(agent_doc_mentions_boundaries=1)

    assert diff.diff_snapshots(_snapshot([old]), _snapshot([new])) == []


def test_diff_snapshots_never_reports_cache_key_itself_as_a_change():
    old = _repo_row(agent_doc_llm_cache_key="CLAUDE.md:sha1")
    new = _repo_row(agent_doc_llm_cache_key="CLAUDE.md:sha2")

    assert diff.diff_snapshots(_snapshot([old]), _snapshot([new])) == []


def test_format_changes_markdown_renders_table():
    changes = [{"repo": "a/a", "field": "has_hooks_config", "old_value": 0, "new_value": 1}]
    markdown = diff.format_changes_markdown("2026-09-13", "2026-09-14", changes)

    assert "2026-09-13" in markdown
    assert "2026-09-14" in markdown
    assert "| a/a | has_hooks_config | 0 | 1 |" in markdown


def test_format_changes_markdown_notes_no_changes():
    markdown = diff.format_changes_markdown("2026-09-13", "2026-09-14", [])
    assert "変化した項目はありませんでした" in markdown


def test_build_report_none_when_fewer_than_two_snapshots(tmp_path):
    (tmp_path / "2026-09-14").mkdir()
    assert diff.build_report(str(tmp_path)) is None


def test_build_report_reads_two_latest_snapshots_and_diffs(tmp_path):
    for date, hooks in [("2026-09-13", 0), ("2026-09-14", 1)]:
        day_dir = tmp_path / date
        day_dir.mkdir()
        snapshot = _snapshot([_repo_row(has_hooks_config=hooks)])
        (day_dir / "metrics.json").write_text(json.dumps(snapshot), encoding="utf-8")

    result = diff.build_report(str(tmp_path))

    assert result is not None
    old_date, new_date, changes, markdown = result
    assert (old_date, new_date) == ("2026-09-13", "2026-09-14")
    assert changes == [
        {"repo": "a/a", "field": "has_hooks_config", "old_value": 0, "new_value": 1}
    ]
    assert "| a/a | has_hooks_config | 0 | 1 |" in markdown
