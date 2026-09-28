import json
import os

import pytest

from agent_trend_radar import llm_content_analysis as llm


class _FakeCompletedProcess:
    def __init__(self, returncode=0, stdout="", stderr=""):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def _fake_runner(response: dict, model_usage: dict | None = None):
    def runner(content: str) -> str:
        payload = {"structured_output": response, "result": ""}
        if model_usage is not None:
            payload["modelUsage"] = model_usage
        return json.dumps(payload)

    return runner


def test_classify_agent_doc_themes_empty_content_short_circuits():
    themes, model_name = llm.classify_agent_doc_themes("")
    assert themes == {field: False for field in llm.CLASSIFICATION_FIELDS}
    assert model_name is None


def test_classify_agent_doc_themes_parses_structured_output():
    response = {
        "agent_doc_mentions_repo_structure": True,
        "agent_doc_mentions_boundaries": False,
        "agent_doc_mentions_pr_review": True,
        "agent_doc_mentions_release_process": False,
    }
    themes, model_name = llm.classify_agent_doc_themes(
        "some content", runner=_fake_runner(response, model_usage={"claude-sonnet-5": {}})
    )
    assert themes == response
    assert model_name == "claude-sonnet-5"


def test_classify_agent_doc_themes_model_name_none_when_model_usage_missing():
    response = {field: False for field in llm.CLASSIFICATION_FIELDS}
    themes, model_name = llm.classify_agent_doc_themes(
        "some content", runner=_fake_runner(response)
    )
    assert themes == response
    assert model_name is None


def test_classify_agent_doc_themes_raises_on_invalid_json():
    def runner(content: str) -> str:
        return "not json"

    with pytest.raises(llm.LLMClassificationError):
        llm.classify_agent_doc_themes("some content", runner=runner)


def test_classify_agent_doc_themes_raises_on_missing_structured_output():
    def runner(content: str) -> str:
        return json.dumps({"result": "no structured_output here"})

    with pytest.raises(llm.LLMClassificationError):
        llm.classify_agent_doc_themes("some content", runner=runner)


def test_classify_agent_doc_themes_raises_on_missing_field():
    def runner(content: str) -> str:
        return json.dumps(
            {"structured_output": {"agent_doc_mentions_repo_structure": True}}
        )

    with pytest.raises(llm.LLMClassificationError):
        llm.classify_agent_doc_themes("some content", runner=runner)


def test_run_claude_cli_uses_empty_cwd_and_disables_tools(monkeypatch, tmp_path):
    """収集対象リポジトリと無関係なradar自身のCLAUDE.md/SPEC.mdが分類コンテキスト
    に混入しないよう、空の一時ディレクトリをcwdにしツールを無効化する(#30, R2)。"""
    captured = {}

    def fake_run(args, **kwargs):
        captured["args"] = args
        captured["kwargs"] = kwargs
        # 一時ディレクトリはwithブロックを抜けると削除されるため、
        # 呼び出しの時点(withブロック内)で存在確認する。
        captured["cwd_existed_during_call"] = os.path.isdir(kwargs.get("cwd", ""))
        return _FakeCompletedProcess(returncode=0, stdout='{"structured_output": {}}')

    monkeypatch.setattr(llm.subprocess, "run", fake_run)

    llm._run_claude_cli("some content")

    assert captured["kwargs"]["cwd"] is not None
    assert captured["cwd_existed_during_call"] is True
    args = captured["args"]
    assert "--tools" in args
    assert args[args.index("--tools") + 1] == ""


def test_run_claude_cli_raises_on_nonzero_exit(monkeypatch):
    def fake_run(args, **kwargs):
        return _FakeCompletedProcess(returncode=1, stdout="", stderr="boom")

    monkeypatch.setattr(llm.subprocess, "run", fake_run)

    with pytest.raises(llm.LLMClassificationError, match="boom"):
        llm._run_claude_cli("some content")


def test_classification_prompt_hash_is_deterministic():
    assert llm.classification_prompt_hash() == llm.classification_prompt_hash()


def test_get_claude_cli_version_returns_stripped_stdout(monkeypatch):
    def fake_run(args, **kwargs):
        assert args == ["claude", "--version"]
        return _FakeCompletedProcess(returncode=0, stdout="2.1.283 (Claude Code)\n")

    monkeypatch.setattr(llm.subprocess, "run", fake_run)

    assert llm.get_claude_cli_version() == "2.1.283 (Claude Code)"


def test_write_and_read_run_metadata_roundtrip(tmp_path):
    path = tmp_path / "llm_run_metadata.json"
    metadata = {"claude_cli_version": "2.1.283", "classification_prompt_hash": "abc"}

    llm.write_run_metadata(metadata, path=str(path))

    assert llm.read_run_metadata(path=str(path)) == metadata


def test_read_run_metadata_returns_empty_dict_when_missing(tmp_path):
    path = tmp_path / "does_not_exist.json"
    assert llm.read_run_metadata(path=str(path)) == {}


def test_extract_model_name_returns_single_key():
    data = {"modelUsage": {"claude-sonnet-5": {"inputTokens": 2}}}
    assert llm.extract_model_name(data) == "claude-sonnet-5"


def test_extract_model_name_joins_multiple_keys_sorted():
    data = {"modelUsage": {"claude-sonnet-5": {}, "claude-haiku-4-5": {}}}
    assert llm.extract_model_name(data) == "claude-haiku-4-5, claude-sonnet-5"


def test_extract_model_name_none_when_missing_or_empty():
    assert llm.extract_model_name({}) is None
    assert llm.extract_model_name({"modelUsage": {}}) is None
    assert llm.extract_model_name({"modelUsage": "not a dict"}) is None


def test_collect_run_metadata_includes_model_name_when_given(monkeypatch):
    monkeypatch.setattr(llm, "get_claude_cli_version", lambda: "2.1.283")
    metadata = llm.collect_run_metadata(model_name="claude-sonnet-5")
    assert metadata["model_name"] == "claude-sonnet-5"


def test_collect_run_metadata_omits_model_name_when_none(monkeypatch):
    monkeypatch.setattr(llm, "get_claude_cli_version", lambda: "2.1.283")
    metadata = llm.collect_run_metadata()
    assert "model_name" not in metadata
