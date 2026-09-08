import publish


def test_repo_to_filename_replaces_slash_with_double_underscore():
    assert publish.repo_to_filename("langchain-ai/langchain") == "langchain-ai__langchain.md"


def test_repo_to_filename_keeps_hyphens_in_owner_and_repo():
    assert publish.repo_to_filename("astral-sh/ruff") == "astral-sh__ruff.md"
