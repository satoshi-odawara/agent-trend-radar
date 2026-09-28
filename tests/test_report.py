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


def test_render_mcp_derived_stats_true_when_count_positive():
    rows = [
        _make_row("a/a", "tool", "commercial_saas", mcp_servers_count=2),
        _make_row("b/b", "tool", "commercial_saas", mcp_servers_count=0),
    ]
    output = report.render_mcp_derived_stats(rows)
    assert "## has_mcp_servers" in output
    assert "| tool | commercial_saas | 2 | 1 | 50% |" in output


def test_render_ff_fb_classification_lists_feedforward_columns():
    output = report.render_ff_fb_classification()
    assert "### フィードフォワード" in output
    for column in report.FEEDFORWARD_COLUMNS:
        assert f"- {column}" in output


def test_render_ff_fb_classification_lists_feedback_columns():
    output = report.render_ff_fb_classification()
    assert "### フィードバック" in output
    for column in report.FEEDBACK_COLUMNS:
        assert f"- {column}" in output


def test_ff_fb_columns_have_no_overlap_or_duplicates():
    assert set(report.FEEDFORWARD_COLUMNS).isdisjoint(report.FEEDBACK_COLUMNS)
    assert len(report.FEEDFORWARD_COLUMNS) == len(set(report.FEEDFORWARD_COLUMNS))
    assert len(report.FEEDBACK_COLUMNS) == len(set(report.FEEDBACK_COLUMNS))


def test_feedback_columns_are_real_check_columns():
    """has_mcp_serversはmcp_servers_countからの派生のためCHECK_COLUMNSには
    存在しない特例。それ以外は実在のCHECK_COLUMNSであること。"""
    for column in report.FEEDBACK_COLUMNS:
        assert column in storage.CHECK_COLUMNS
    for column in report.FEEDFORWARD_COLUMNS:
        if column == "has_mcp_servers":
            continue
        assert column in storage.CHECK_COLUMNS


def test_render_stats_includes_new_sections_without_breaking_existing():
    rows = [_make_row("a/a", "tool", "commercial_saas", has_ci=True, mcp_servers_count=1)]
    output = report.render_stats(rows)
    assert "## has_ci" in output
    assert "## has_mcp_servers" in output
    assert "## フィードフォワード/フィードバックの分類" in output
