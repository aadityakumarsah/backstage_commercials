import os
from openai import OpenAI
import dotenv

dotenv.load_dotenv()

gemini_key = os.getenv("GEMINI_API_KEY")
openrouter_key = os.getenv("OPENROUTER_API_KEY")

if gemini_key:
    client = OpenAI(
        api_key=gemini_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    )
    MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
elif openrouter_key:
    client = OpenAI(
        api_key=openrouter_key,
        base_url="https://openrouter.ai/api/v1",
    )
    MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-2.0-flash-exp:free")
else:
    raise RuntimeError(
        "No API key found. Set GEMINI_API_KEY or OPENROUTER_API_KEY in .env"
    )
