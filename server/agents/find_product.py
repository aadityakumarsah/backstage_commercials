import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
)
MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-3.1-flash-lite-preview")


def ask_search_product_agent(input_image: str, text_prompt: str) -> dict:
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a product discovery assistant. Given an image and a user prompt, "
                    "identify the requested product and search your knowledge for Amazon links. "
                    "Return valid JSON only with the schema below."
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": text_prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": input_image},
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
    )
    raw = response.choices[0].message.content
    return json.loads(raw)
