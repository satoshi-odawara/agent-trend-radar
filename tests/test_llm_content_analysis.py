import json

import pytest

from agent_trend_radar import llm_content_analysis as llm


def _fake_runner(response: dict):
    def runner(content: str) -> str:
        return json.dumps({"structured_output": response, "result": ""})

    return runner


def test_classify_agent_doc_themes_empty_content_short_circuits():
    result = llm.classify_agent_doc_themes("")
    assert result == {field: False for field in llm.CLASSIFICATION_FIELDS}


def test_classify_agent_doc_themes_parses_structured_output():
    response = {
        "agent_doc_mentions_repo_structure": True,
        "agent_doc_mentions_boundaries": False,
        "agent_doc_mentions_pr_review": True,
        "agent_doc_mentions_release_process": False,
    }
    result = llm.classify_agent_doc_themes("some content", runner=_fake_runner(response))
    assert result == response


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
