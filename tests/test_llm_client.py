import pytest

from llm.llm_client import LLMClient


def test_empty_prompt_raises_error():

    client = LLMClient()

    with pytest.raises(ValueError):
        client.generate_answer("")