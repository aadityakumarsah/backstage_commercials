import os
import uuid
import base64
import json
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename

from server.agents.find_product import ask_search_product_agent
from server.agents.add_to_cart import ask_add_to_shopping_cart
from server.agents.search_similar import ask_search_similar_agent

load_dotenv()

app = Flask(__name__)

origins = os.getenv("CORS_ORIGINS", "*")
CORS(app, origins=origins.split(","))

TMP_DIR = Path(os.getenv("TMP_IMAGES_DIR", "./tmp_images"))
TMP_DIR.mkdir(parents=True, exist_ok=True)

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

RENDER_DIR = Path("./renders")
RENDER_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_VIDEO = {"mp4", "mov", "avi", "webm", "mkv"}
ALLOWED_IMAGE = {"png", "jpg", "jpeg", "webp"}


def _ext( filename: str) -> str:
    return filename.rsplit(".", 1)[-1].lower() if "." in filename else ""


def to_data_url(filename: str, mime_type: str = "image/jpeg") -> str:
    filepath = TMP_DIR / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Image not found: {filepath}")
    data = base64.b64encode(filepath.read_bytes()).decode("utf-8")
    return f"data:{mime_type};base64,{data}"


# ---------------------------------------------------------------------------
# Render jobs — in-memory store (swap for DB/Redis in production)
# ---------------------------------------------------------------------------
RENDER_JOBS: dict[str, dict] = {}


@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({"error": str(error)}), 500


@app.post("/render")
def create_render():
    if "video" not in request.files:
        return jsonify({"error": "video file is required"}), 400
    if "product_image" not in request.files:
        return jsonify({"error": "product_image file is required"}), 400

    video = request.files["video"]
    product_img = request.files["product_image"]
    product_name = request.form.get("product_name", "Product")
    product_desc = request.form.get("product_description", "")
    product_price = request.form.get("product_price", "")

    ve = _ext(video.filename)
    pe = _ext(product_img.filename)
    if ve not in ALLOWED_VIDEO:
        return jsonify({"error": f"Unsupported video format: .{ve}"}), 400
    if pe not in ALLOWED_IMAGE:
        return jsonify({"error": f"Unsupported image format: .{pe}"}), 400

    job_id = uuid.uuid4().hex[:12]

    video_name = secure_filename(f"{job_id}_video.{ve}")
    product_name_f = secure_filename(f"{job_id}_product.{pe}")
    video.save(str(UPLOAD_DIR / video_name))
    product_img.save(str(UPLOAD_DIR / product_name_f))

    RENDER_JOBS[job_id] = {
        "job_id": job_id,
        "status": "uploaded",
        "video_path": str(UPLOAD_DIR / video_name),
        "product_path": str(UPLOAD_DIR / product_name_f),
        "product_name": product_name,
        "product_description": product_desc,
        "product_price": product_price,
        "created_at": datetime.utcnow().isoformat(),
        "output_url": None,
    }

    return jsonify({"job_id": job_id, "status": "uploaded"})


@app.get("/render/status/<job_id>")
def render_status(job_id: str):
    job = RENDER_JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    return jsonify({
        "job_id": job["job_id"],
        "status": job["status"],
        "progress": job.get("progress", 0),
        "created_at": job["created_at"],
    })


@app.get("/render/result/<job_id>")
def render_result(job_id: str):
    job = RENDER_JOBS.get(job_id)
    if not job:
        return jsonify({"error": "Job not found"}), 404
    if job["status"] != "completed":
        return jsonify({"error": "Job not yet completed", "status": job["status"]}), 400

    return jsonify({
        "job_id": job["job_id"],
        "status": "completed",
        "video_url": job.get("output_url"),
    })


@app.get("/renders/<path:filename>")
def serve_render(filename: str):
    return send_from_directory(RENDER_DIR, filename)


# ---------------------------------------------------------------------------
# Existing agent endpoints
# ---------------------------------------------------------------------------

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
