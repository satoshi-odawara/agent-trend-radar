import re
import sys

import report

from agent_trend_radar import storage

SCHEMA_SECTION_HEADING = "## `repos` の各要素"
FIELD_ROW_PATTERN = re.compile(r"^\|\s*`([A-Za-z0-9_]+)`\s*\|")


def extract_schema_fields(schema_md: str) -> set[str]:
    """SCHEMA.mdの「`repos` の各要素」セクションのテーブルからフィールド名を抽出する。"""
    lines = schema_md.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == SCHEMA_SECTION_HEADING)
    except StopIteration:
        raise SystemExit(
            f"SCHEMA.mdに '{SCHEMA_SECTION_HEADING}' セクションが見つかりません。"
            "SCHEMA.mdの見出し構成が変わっていないか確認してください。"
        )

    fields = set()
    for line in lines[start + 1 :]:
        if line.startswith("## "):
            break
        match = FIELD_ROW_PATTERN.match(line.strip())
        if match:
            fields.add(match.group(1))
    return fields


def find_mismatches(check_columns: list[str], documented_fields: set[str]) -> tuple[set[str], set[str]]:
    """(SCHEMA.mdに未記載のフィールド, CHECK_COLUMNSに存在しないのにSCHEMA.mdに残っているフィールド)を返す。"""
    expected = set(check_columns)
    meta_only = documented_fields - expected - set(report.META_COLUMNS)
    missing_in_schema = expected - documented_fields
    return missing_in_schema, meta_only


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    if len(sys.argv) != 2:
        print("usage: uv run scripts/check_hub_schema_sync.py <schema_md_path>", file=sys.stderr)
        raise SystemExit(1)
    schema_path = sys.argv[1]

    with open(schema_path, encoding="utf-8") as f:
        schema_md = f.read()

    documented_fields = extract_schema_fields(schema_md)
    missing_in_schema, stale_in_schema = find_mismatches(storage.CHECK_COLUMNS, documented_fields)

    if missing_in_schema or stale_in_schema:
        if missing_in_schema:
            print(
                f"SCHEMA.mdに未記載のフィールドがあります: {sorted(missing_in_schema)}",
                file=sys.stderr,
            )
        if stale_in_schema:
            print(
                f"CHECK_COLUMNSに存在しないのにSCHEMA.mdに記載が残っているフィールドがあります: "
                f"{sorted(stale_in_schema)}",
                file=sys.stderr,
            )
        raise SystemExit(1)

    print(f"{schema_path} は storage.CHECK_COLUMNS と一致しています。")


if __name__ == "__main__":
    main()
