import check_hub_schema_sync

from agent_trend_radar import storage

SAMPLE_SCHEMA_MD = """\
# SCHEMA

## `metrics.json`

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `generated_at` | string | ... |
| `repos` | array<object> | ... |

## `repos` の各要素

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `repo` | string | ... |
| `segment` | string (enum) | ... |
| `monetization_model` | string (enum) | ... |
| `has_agent_instructions` | 0 or 1 | ... |

## `manifest.json`

| フィールド | 型 | 説明 |
| --- | --- | --- |
| `dates` | array<string> | ... |
"""


def test_extract_schema_fields_scopes_to_repos_section_only():
    fields = check_hub_schema_sync.extract_schema_fields(SAMPLE_SCHEMA_MD)
    assert fields == {"repo", "segment", "monetization_model", "has_agent_instructions"}
    assert "generated_at" not in fields
    assert "dates" not in fields


def test_extract_schema_fields_raises_when_section_missing():
    try:
        check_hub_schema_sync.extract_schema_fields("# SCHEMA\n\nno sections here\n")
    except SystemExit:
        pass
    else:
        raise AssertionError("SystemExitが発生するはず")


def test_find_mismatches_none_when_in_sync():
    documented = set(storage.CHECK_COLUMNS) | {"repo", "segment", "monetization_model"}
    missing, stale = check_hub_schema_sync.find_mismatches(storage.CHECK_COLUMNS, documented)
    assert missing == set()
    assert stale == set()


def test_find_mismatches_detects_field_missing_from_schema():
    documented = set(storage.CHECK_COLUMNS) - {"has_hooks_config"} | {
        "repo",
        "segment",
        "monetization_model",
    }
    missing, stale = check_hub_schema_sync.find_mismatches(storage.CHECK_COLUMNS, documented)
    assert missing == {"has_hooks_config"}
    assert stale == set()


def test_find_mismatches_detects_stale_field_in_schema():
    documented = set(storage.CHECK_COLUMNS) | {
        "repo",
        "segment",
        "monetization_model",
        "has_removed_field",
    }
    missing, stale = check_hub_schema_sync.find_mismatches(storage.CHECK_COLUMNS, documented)
    assert missing == set()
    assert stale == {"has_removed_field"}
