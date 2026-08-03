import pytest

from llm.prompt_builder import PromptBuilder


sample_chunks = [
    {
        "file_path": "auth.py",
        "start_line": 10,
        "end_line": 35,
        "content": "def authenticate(user): ...",
        "score": 0.91,
    },
    {
        "file_path": "jwt.py",
        "start_line": 5,
        "end_line": 18,
        "content": "def create_token(): ...",
        "score": 0.87,
    },
]


def test_build_prompt_returns_string():

    prompt = PromptBuilder.build_prompt(
        "Where is authentication implemented?",
        sample_chunks,
    )

    assert isinstance(prompt, str)


def test_prompt_contains_query():

    prompt = PromptBuilder.build_prompt(
        "authentication",
        sample_chunks,
    )

    assert "authentication" in prompt


def test_prompt_contains_repository_context():

    prompt = PromptBuilder.build_prompt(
        "authentication",
        sample_chunks,
    )

    assert "auth.py" in prompt
    assert "jwt.py" in prompt


def test_empty_query_raises_error():

    with pytest.raises(ValueError):
        PromptBuilder.build_prompt(
            "",
            sample_chunks,
        )


def test_empty_chunks_raise_error():

    with pytest.raises(ValueError):
        PromptBuilder.build_prompt(
            "authentication",
            [],
        )