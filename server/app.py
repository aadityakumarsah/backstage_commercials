import os
import base64
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS

from server.agents.find_product import ask_search_product_agent
from server.agents.add_to_cart import ask_add_to_shopping_cart
from server.agents.search_similar import ask_search_similar_agent

load_dotenv()

app = Flask(__name__)

origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, origins=origins.split(","))

TMP_DIR = Path(os.getenv("TMP_IMAGES_DIR", "./tmp_images"))
TMP_DIR.mkdir(parents=True, exist_ok=True)


def to_data_url(filename: str, mime_type: str = "image/jpeg") -> str:
    filepath = TMP_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Image not found: {filepath}")
    data = base64.b64encode(filepath.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{data}"


@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({"error": str(error)}), 500


@app.post("/find-it-on-amazon")
def find_it_on_amazon():
    data = request.get_json(force=True)
    frame_url = data.get("image_url")
    if not frame_url:
        return jsonify({"error": "image_url is required"}), 400

    frame = to_data_url(frame_url)
    text_prompt = data.get("user_prompt", "Find this product on Amazon")
    return ask_search_product_agent(input_image=frame, text_prompt=text_prompt)


@app.post("/select-similar-from-amazon")
def select_similar_from_amazon():
    data = request.get_json(force=True)
    product_description = data.get("product_description")
    if not product_description:
        return jsonify({"error": "product_description is required"}), 400

    links = ask_search_similar_agent(product_description, k=2)
    return {"amazon_links": links}


@app.post("/select-similar-from-amazon/add_to_list")
def select_similar_from_amazon_and_add_to_list():
    data = request.get_json(force=True)
    product_description = data.get("product_description")
    if not product_description:
        return jsonify({"error": "product_description is required"}), 400

    links = ask_search_similar_agent(product_description, k=1)
    return {"amazon_links": links}


@app.route("/add-it-to-shopping-cart", methods=["POST"])
def add_it_to_shopping_cart():
    data = request.get_json(force=True)
    product_url = data.get("product_url")
    if not product_url:
        return jsonify({"error": "product_url is required"}), 400

    result = ask_add_to_shopping_cart(product_url)
    return {"agent_finished": result}


@app.route("/add-it-to-shopping-list", methods=["POST"])
def add_it_to_shopping_list():
    data = request.get_json(force=True)
    product_url = data.get("product_url")
    if not product_url:
        return jsonify({"error": "product_url is required"}), 400

    result = ask_add_to_shopping_cart(product_url, add_to_wishlist="wishlist")
    return {"agent_finished": result}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
