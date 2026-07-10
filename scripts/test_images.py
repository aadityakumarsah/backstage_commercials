import os
import base64
import mimetypes
from ml._llm import client, MODEL


def encode_image(path):
    mime = mimetypes.guess_type(path)[0]
    with open(path, "rb") as f:
        data = base64.b64encode(f.read()).decode()
    return mime, data


system_prompt = """
You are an AI product discovery assistant.

Your task is to analyze the provided image and identify objects that correspond to consumer products that could realistically be sold on Amazon.

IMPORTANT: The product names must be simple and compatible with common object detection classes (such as YOLO). This means the name should usually be 1-2 words describing the object type.

Instructions:

1. Carefully inspect the image and detect objects that correspond to real consumer products.
2. Only include objects that could realistically be purchased online (electronics, furniture, clothing, home goods, accessories, tools, kitchen items, etc.).
3. Ignore objects that are not purchasable products (people, buildings, sky, animals, scenery, etc.).
4. For each detected product:
   - Provide a **simple object name (1-2 words)** that corresponds to a common detection class (examples: laptop, mug, keyboard, chair, backpack, lamp).
   - If multiple similar objects exist, add a **color or simple distinguishing attribute** to the name (example: "green teapot", "yellow teapot", "black mug").
   - Do NOT include long descriptions in the name.
5. Provide additional information in separate fields:
   - category: a short product category.
   - properties: short product attributes such as color, size, material, or visible features.
   - reason: why this product may be interesting for a user to purchase.

Naming Rules:
- Prefer common YOLO-style object names.
- Use lowercase names.
- Keep names concise (1-2 words, optionally with a color).

Return the result strictly in the following JSON format:

{
  "products": [
    {
      "name": "product name",
      "category": "product category",
      "properties": "product properties",
      "reason": "why this product might interest the user"
    }
  ]
}

Only output JSON.
"""

image_path = "hs.png"
mime, base64_image = encode_image(image_path)

response = client.chat.completions.create(
    model=MODEL,
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "List all products visible in this image."},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{base64_image}"}},
            ],
        },
    ],
    max_tokens=800,
)

print(response.choices[0].message.content)
