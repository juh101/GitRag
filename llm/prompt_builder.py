from typing import Any


class PromptBuilder:
    """
    Builds prompts for the LLM using the retrieved repository chunks.
    """

    SYSTEM_PROMPT = """
You are an expert software engineer.

Answer the user's question ONLY using the provided repository context.

If the answer cannot be determined from the context, clearly say that the repository context does not contain enough information.

Always mention the file names whenever possible.

Be concise, accurate, and technical.
""".strip()

    @classmethod
    def build_prompt(
        cls,
        query: str,
        retrieved_chunks: list[dict[str, Any]],
    ) -> str:
        """
        Build the complete prompt sent to the LLM.
        """

        if not query.strip():
            raise ValueError("Query cannot be empty.")

        if not retrieved_chunks:
            raise ValueError("No retrieved chunks were provided.")

        context_sections = []

        for chunk in retrieved_chunks:

            section = f"""
File:
{chunk["file_path"]}

Lines:
{chunk["start_line"]}-{chunk["end_line"]}

Similarity Score:
{chunk["score"]:.4f}

Content:
{chunk["content"]}
"""

            context_sections.append(section.strip())

        repository_context = "\n\n" + ("-" * 80) + "\n\n"

        repository_context = repository_context.join(context_sections)

        prompt = f"""
{cls.SYSTEM_PROMPT}

Repository Context

{repository_context}

User Question

{query}

Answer:
"""

        return prompt.strip()