import os

from dotenv import load_dotenv
from google import genai


load_dotenv()


class LLMClient:
    """
    Wrapper around the Gemini API.

    Responsible only for sending prompts to the LLM
    and returning the generated response.
    """

    DEFAULT_MODEL = "gemini-2.5-flash"

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL,
    ) -> None:

        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError(
                "GEMINI_API_KEY not found in environment variables."
            )

        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name

    def generate_answer(
        self,
        prompt: str,
    ) -> str:
        """
        Send a prompt to Gemini and return the generated text.
        """

        if not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
        )

        if response.text is None:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()