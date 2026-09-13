import json

import update_hub_manifest


def test_load_manifest_defaults_when_missing(tmp_path):
    path = tmp_path / "manifest.json"
    assert update_hub_manifest.load_manifest(str(path)) == {"dates": []}


def test_load_manifest_reads_existing_file(tmp_path):
    path = tmp_path / "manifest.json"
    path.write_text(json.dumps({"dates": ["2026-09-01"]}), encoding="utf-8")
    assert update_hub_manifest.load_manifest(str(path)) == {"dates": ["2026-09-01"]}


def test_add_date_appends_and_sorts():
    manifest = {"dates": ["2026-09-08"]}
    result = update_hub_manifest.add_date(manifest, "2026-09-01")
    assert result["dates"] == ["2026-09-01", "2026-09-08"]


def test_add_date_dedupes_existing_date():
    manifest = {"dates": ["2026-09-01"]}
    result = update_hub_manifest.add_date(manifest, "2026-09-01")
    assert result["dates"] == ["2026-09-01"]
