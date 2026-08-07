import os
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class LLMClient:
    """
    Wrapper around the Gemini API.

    Responsible only for sending prompts to the LLM
    and returning the generated response.
    """

    DEFAULT_MODEL = "gemini-flash-lite-latest"

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
        temperature: float = 0.2,
    ) -> str:

        print("=" * 80)
        print(f"Model: {self.model_name} | Temperature: {temperature}")
        print(f"Prompt length: {len(prompt)}")
        print("=" * 80)

        print(prompt[:1000])

        print("=" * 80)

        config = types.GenerateContentConfig(
            temperature=temperature
        )

        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=config,
        )

        if response.text is None:
            raise RuntimeError("Gemini returned an empty response.")

        return response.text.strip()