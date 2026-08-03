from retrieval.vector_retriever import VectorRetriever
from llm.prompt_builder import PromptBuilder
from llm.llm_client import LLMClient


class AnswerGenerator:
    """
    Coordinates the complete RAG pipeline.

    It does not know HOW retrieval or LLM works.
    It simply connects all components together.
    """

    def __init__(
        self,
        retriever: VectorRetriever,
        prompt_builder: PromptBuilder,
        llm_client: LLMClient,
    ) -> None:

        self.retriever = retriever
        self.prompt_builder = prompt_builder
        self.llm_client = llm_client

    def answer_question(
        self,
        question: str,
        top_k: int = 5,
    ) -> str:

        if not question.strip():
            raise ValueError("Question cannot be empty.")

        retrieved_chunks = self.retriever.retrieve(
            question,
            top_k,
        )

        prompt = self.prompt_builder.build_prompt(
            question,
            retrieved_chunks,
        )

        answer = self.llm_client.generate_answer(
            prompt,
        )

        return answer 