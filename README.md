# BackstageCommercials

A framework for embedding personalized product placements into movies and TV shows. Uses AI vision models to identify placement surfaces, generative models to blend products into scenes, and browser automation to enable one-click shopping.

## Architecture

```
backstage_commercials/
├── client/              # React frontend (Prime Video-style UI)
│   └── prime-video-ui/
│       ├── src/
│       └── public/
├── server/              # Flask API + shopping agents
│   ├── app.py           # API entry point (routes)
│   └── agents/          # Agent modules
│       ├── find_product.py      # LLM-based product discovery
│       ├── search_similar.py    # Amazon search automation
│       ├── add_to_cart.py       # Cart/wishlist automation
│       └── browser_agent.py     # Playwright browser driver
├── ml/                  # ML pipeline (GPU recommended)
│   ├── select_frame.py  # Scene cut detection & shot scoring
│   ├── insert_product.py# Recursive placement with LLM feedback
│   ├── generate_video.py# YOLO-based person masking & frame compositing
│   ├── flux.py          # FLUX Kontext model integration
│   └── pipeline.py      # End-to-end pipeline orchestrator
├── scripts/             # Standalone test & utility scripts
├── .env                 # Local environment configuration
└── requirements.txt     # Python dependencies
```

## Tech Stack

| Layer | Technology | Hosting |
|---|---|---|
| **Frontend** | React 19, Vite, CSS-in-JS | Vercel / Netlify |
| **API Server** | Python 3.11+, Flask, Flask-CORS | Render / Railway |
| **LLM Provider** | OpenRouter (Gemini, Claude) | External API |
| **Browser Automation** | Playwright (Chromium) | Bundled with server |
| **ML Pipeline** | OpenCV, PyTorch, FLUX, YOLOv8, Ultralytics | GPU instance |
| **Image Processing** | Pillow, NumPy | Bundled with ML |

## Prerequisites

- Python 3.11+
- Node.js 18+
- An [OpenRouter](https://openrouter.ai) API key (free tier available)

## Quick Start

### 1. Environment

```bash
cp .env.example .env
```

Edit `.env` and set your `OPENROUTER_API_KEY`.

### 2. Backend

```bash
pip install -r requirements.txt
playwright install chromium

python -m server.app
```

The API starts on `http://0.0.0.0:8000`.

### 3. Frontend

```bash
cd client/prime-video-ui
npm install
npm run dev
```

Opens on `http://localhost:5173`.

## Configuration

All configuration is through environment variables (`.env`):

| Variable | Default | Description |
|---|---|---|
| `OPENROUTER_API_KEY` | — | OpenRouter API key (required) |
| `OPENROUTER_MODEL` | `google/gemini-3.1-flash-lite-preview` | LLM for vision & text tasks |
| `BROWSER_HEADLESS` | `true` | Run Playwright in headless mode |
| `AMAZON_DOMAIN` | `https://www.amazon.ca` | Amazon marketplace domain |
| `CORS_ORIGINS` | `*` | Allowed CORS origins (comma-separated) |
| `TMP_IMAGES_DIR` | `./tmp_images` | Directory for uploaded frame images |

## API Reference

### `POST /find-it-on-amazon`

Identifies a product in an image and returns Amazon links.

**Request:**
```json
{
  "image_url": "frame_001.jpg",
  "user_prompt": "Find this coffee table on Amazon"
}
```

**Response:** JSON object with `amazon_link`, `item_description`, `is_found`.

### `POST /select-similar-from-amazon`

Searches Amazon for products matching a description.

**Request:**
```json
{
  "product_description": "wooden coffee table"
}
```

**Response:**
```json
{ "amazon_links": ["https://www.amazon.ca/...", ...] }
```

### `POST /add-it-to-shopping-cart`

Opens a product URL and clicks "Add to Cart".

**Request:**
```json
{ "product_url": "https://www.amazon.ca/..." }
```

**Response:**
```json
{ "agent_finished": true }
```

### `POST /add-it-to-shopping-list`

Opens a product URL and adds it to the wishlist.

**Request:**
```json
{ "product_url": "https://www.amazon.ca/..." }
```

## ML Pipeline (GPU Required)

The full product-placement pipeline processes a video end-to-end:

```bash
pip install -r requirements-gpu.txt
python -m ml.pipeline <video.mp4> <product.png> "Product Description"
```

Steps:
1. **Scene detection** — OpenCV histogram + homography analysis finds stable shots
2. **LLM shot scoring** — Vision model rates each shot for placement suitability
3. **Bounding box prediction** — Recursive LLM placement with evaluation model feedback
4. **Frame compositing** — FLUX Kontext model blends the product into the first frame
5. **Frame propagation** — Product patch is carried across frames with YOLO person masking

## Deployment

### Server (Render / Railway)

```dockerfile
FROM python:3.11-slim
RUN pip install -r requirements.txt && playwright install chromium
COPY . .
CMD ["python", "-m", "server.app"]
```

### Frontend (Vercel)

```
Build command: cd client/prime-video-ui && npm run build
Output dir: client/prime-video-ui/dist
```

### ML Pipeline (GPU)

The ML pipeline requires a GPU with 24 GB+ VRAM for FLUX inference. Deploy via:

- [RunPod](https://runpod.io) — serverless GPU
- [Replicate](https://replicate.com) — model hosting
- Self-hosted with Docker + NVIDIA container toolkit

## Migration from Amazon Nova

This project originally used Amazon Nova models and NovaAct for browser automation. It has been migrated to:

| Original | Replacement |
|---|---|
| `AMZN Nova 2 Lite` (vision LLM) | `google/gemini-3.1-flash-lite-preview` via OpenRouter |
| `NovaAct` (browser agent) | Playwright (Chromium) |
| `NOVA_API_KEY` | `OPENROUTER_API_KEY` |

## Development

```bash
# Run linting
cd client/prime-video-ui && npm run lint

# Run standalone test
python -m scripts.test_images
```

## License

MIT
