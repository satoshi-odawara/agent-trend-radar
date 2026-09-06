from agent_trend_radar import config


def test_load_targets_returns_list_of_dicts(tmp_path):
    targets_file = tmp_path / "targets.yaml"
    targets_file.write_text(
        "targets:\n"
        "  - repo: owner/repo-a\n"
        "    segment: tool\n"
        "    monetization_model: commercial_saas\n"
        "  - repo: owner/repo-b\n"
        "    segment: adopter\n"
        "    monetization_model: individual_community\n",
        encoding="utf-8",
    )

    targets = config.load_targets(str(targets_file))

    assert targets == [
        {
            "repo": "owner/repo-a",
            "segment": "tool",
            "monetization_model": "commercial_saas",
        },
        {
            "repo": "owner/repo-b",
            "segment": "adopter",
            "monetization_model": "individual_community",
        },
    ]


def test_load_targets_default_path_reads_real_config():
    targets = config.load_targets()

    assert len(targets) == 20
    assert all({"repo", "segment", "monetization_model"} <= t.keys() for t in targets)
