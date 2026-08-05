import pytest

from llm.answer_generator import AnswerGenerator


class FakeRetriever:
    """
    Fake retriever used for testing.
    """

    def retrieve(
        self,
        query: str,
        top_k: int,
    ):
        return [
            {
                "file_path": "auth.py",
                "start_line": 10,
                "end_line": 20,
                "content": "def authenticate(user): ...",
                "score": 0.95,
            }
        ]


class FakePromptBuilder:
    """
    Fake prompt builder used for testing.
    """

    def build_prompt(
        self,
        query: str,
        retrieved_chunks,
    ):
        return f"Prompt for: {query}"


class FakeLLMClient:
    """
    Fake LLM client used for testing.
    """

    def generate_answer(
        self,
        prompt: str,
    ):
        return "This is a fake answer."


@pytest.fixture
def answer_generator():

    retriever = FakeRetriever()

    prompt_builder = FakePromptBuilder()

    llm_client = FakeLLMClient()

    return AnswerGenerator(
        retriever,
        prompt_builder,
        llm_client,
    )


def test_empty_question_raises_error(
    answer_generator,
):

    with pytest.raises(ValueError):
        answer_generator.answer_question("")


def test_answer_returns_string(
    answer_generator,
):

    answer = answer_generator.answer_question(
        "Where is authentication implemented?"
    )

    assert isinstance(answer, str)


def test_answer_matches_fake_llm(
    answer_generator,
):

    answer = answer_generator.answer_question(
        "Where is authentication implemented?"
    )

    assert answer == "This is a fake answer."