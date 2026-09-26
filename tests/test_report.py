import report

from agent_trend_radar import storage


def _make_row(repo: str, segment: str, monetization_model: str, **overrides) -> tuple:
    values = {col: 0 for col in report.NUMERIC_COLUMNS}
    values.update({col: False for col in storage.CHECK_COLUMNS if col not in report.NUMERIC_COLUMNS})
    values.update(overrides)
    return (
        repo,
        segment,
        monetization_model,
        *(values[col] for col in storage.CHECK_COLUMNS),
    )


def test_render_boolean_stats_reports_count_and_rate():
    rows = [
        _make_row("a/a", "tool", "commercial_saas", has_ci=True),
        _make_row("b/b", "tool", "commercial_saas", has_ci=True),
        _make_row("c/c", "tool", "commercial_saas", has_ci=False),
    ]
    output = report.render_boolean_stats(rows)
    assert "## has_ci" in output
    assert "| tool | commercial_saas | 3 | 2 | 67% |" in output


def test_render_boolean_stats_covers_new_llm_columns():
    rows = [
        _make_row("a/a", "tool", "commercial_saas", agent_doc_mentions_boundaries=True),
    ]
    output = report.render_boolean_stats(rows)
    assert "## agent_doc_mentions_boundaries" in output
    assert "| tool | commercial_saas | 1 | 1 | 100% |" in output


def test_render_boolean_stats_excludes_numeric_columns():
    rows = [_make_row("a/a", "tool", "commercial_saas")]
    output = report.render_boolean_stats(rows)
    assert "## agent_doc_char_count" not in output
    assert "## agent_doc_heading_count" not in output


def test_render_boolean_stats_excludes_text_columns():
    """agent_doc_llm_cache_keyは文字列(#30)であり、bool()に通すと非空文字列
    が常にtrue扱いになってしまうため、真偽値集計の対象から除外する。"""
    rows = [_make_row("a/a", "tool", "commercial_saas", agent_doc_llm_cache_key="CLAUDE.md:sha1")]
    output = report.render_boolean_stats(rows)
    assert "## agent_doc_llm_cache_key" not in output


def test_format_cell_renders_text_column_as_raw_string():
    assert report.format_cell("agent_doc_llm_cache_key", "CLAUDE.md:sha1") == "CLAUDE.md:sha1"
    assert report.format_cell("agent_doc_llm_cache_key", "") == ""
