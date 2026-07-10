import os
import sys
import json
import time
import shutil
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from threading import Thread

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ml.select_frame import find_best_product_placement_shot
from ml.insert_product import recursive_placement

RENDER_DIR = Path(__file__).resolve().parent.parent / "renders"
RENDER_DIR.mkdir(parents=True, exist_ok=True)

try:
    from ultralytics import YOLO
    _yolo = YOLO("yolov8n-seg.pt")
    _yolo_available = True
except Exception:
    _yolo_available = False


def _simple_composite(
    video_path: str,
    begin_frame: int,
    end_frame: int,
    product_img_path: str,
    bbox_pixels: dict,
    output_path: str,
) -> str:
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    x1 = max(0, min(bbox_pixels["x1"], w - 1))
    y1 = max(0, min(bbox_pixels["y1"], h - 1))
    x2 = max(0, min(bbox_pixels["x2"], w))
    y2 = max(0, min(bbox_pixels["y2"], h))
    if x2 <= x1 or y2 <= y1:
        print(f"Invalid bbox after clip ({x1},{y1})-({x2},{y2}) for video ({w}x{h}), copying original")
        shutil.copy2(video_path, output_path)
        cap.release()
        return str(output_path)

    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    writer = cv2.VideoWriter(str(output_path), cv2.CAP_FFMPEG, fourcc, fps, (w, h))
    if not writer.isOpened():
        fallback_fcc = cv2.VideoWriter_fourcc(*"mp4v")
        writer = cv2.VideoWriter(str(output_path), fallback_fcc, fps, (w, h))

    prod_pil = Image.open(product_img_path).convert("RGBA")
    pw, ph = x2 - x1, y2 - y1
    prod_resized = prod_pil.resize((pw, ph), Image.Resampling.LANCZOS)

    cap.set(cv2.CAP_PROP_POS_FRAMES, begin_frame)
    for _ in range(begin_frame, end_frame + 1):
        ok, frame = cap.read()
        if not ok:
            break

        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
        frame_pil.paste(prod_resized, (x1, y1), prod_resized)
        out = cv2.cvtColor(np.array(frame_pil.convert("RGB")), cv2.COLOR_RGB2BGR)
        writer.write(out)

    cap.release()
    writer.release()
    return str(output_path)


def _composite_with_yolo(
    video_path: str,
    begin_frame: int,
    end_frame: int,
    placed_image_path: str,
    bbox_pixels: dict,
    output_path: str,
) -> str:
    from ml.generate_video import generate_video
    return generate_video(
        filename=placed_image_path,
        video_path=video_path,
        begin_frame=begin_frame,
        end_frame=end_frame,
        product_bbox=(bbox_pixels["x1"], bbox_pixels["y1"], bbox_pixels["x2"], bbox_pixels["y2"]),
        output_path=str(output_path),
        person_expand_px=4,
        feather_px=3,
        edge_smooth_px=3,
        recover_original_under_person=0.85,
        recover_blur_ksize=3,
    )


def _composite_frames(
    video_path: str,
    begin_frame: int,
    end_frame: int,
    product_img_path: str,
    placed_image_path: str,
    bbox_pixels: dict,
    output_path: str,
) -> str:
    if _yolo_available:
        try:
            return _composite_with_yolo(
                video_path, begin_frame, end_frame,
                placed_image_path, bbox_pixels, output_path,
            )
        except Exception as e:
            print(f"YOLO composite failed ({e}), falling back to simple composite")
    return _simple_composite(
        video_path, begin_frame, end_frame,
        product_img_path, bbox_pixels, output_path,
    )


def _get_frame_range(video_path: str) -> tuple:
    cap = cv2.VideoCapture(video_path)
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    cap.release()
    max_frames = int(fps * 10)
    return 0, min(total - 1, max_frames) if total > 0 else 149


def run_job(job: dict, status_callback):
    job_id = job["job_id"]
    video_path = job["video_path"]
    product_path = job["product_path"]
    product_desc = job.get("product_description") or job.get("product_name", "Product")

    try:
        # Step 1 — select frame
        status_callback(job_id, "analyzing", 5, "Analyzing scene structure")
        shot = find_best_product_placement_shot(video_path=video_path)
        begin_frame = shot.get("best_shot_start_frame")
        end_frame = shot.get("best_shot_end_frame")

        # Fallback: if scene analysis finds no suitable shot, use first 10 seconds
        if begin_frame is None:
            status_callback(
                job_id, "extracting", 10,
                "No clear shot boundaries found — using full video window",
            )
            begin_frame, end_frame = _get_frame_range(video_path)

        # Step 2 — extract the reference frame (middle of the chosen window)
        status_callback(job_id, "extracting", 15, "Extracting placement frame")
        cap = cv2.VideoCapture(video_path)
        mid_frame = (begin_frame + end_frame) // 2
        cap.set(cv2.CAP_PROP_POS_FRAMES, mid_frame)
        ok, frame = cap.read()
        cap.release()
        if not ok:
            raise RuntimeError(f"Failed to read frame {mid_frame}")
        background_path = str(RENDER_DIR / f"{job_id}_background.png")
        cv2.imwrite(background_path, frame)

        # Step 3 — product placement (LLM)
        status_callback(job_id, "placing", 30, "Positioning product in scene")
        placed_image, bbox_coords = recursive_placement(
            background_path, product_path, product_desc, max_iters=4,
        )
        if bbox_coords is None:
            # Fallback: place product at center of frame at 20% size
            h, w = frame.shape[:2]
            margin = 0.3
            pw, ph = int(w * 0.2), int(h * 0.2)
            cx, cy = int(w * 0.5), int(h * 0.45)
            bbox_coords = {
                "x1": cx - pw // 2, "y1": cy - ph // 2,
                "x2": cx + pw // 2, "y2": cy + ph // 2,
            }
            placed_image = background_path
            status_callback(job_id, "placing", 30, "Using default placement (LLM could not find optimal position)")

        # Step 4 — composite across frames
        status_callback(job_id, "rendering", 55, "Rendering output video")
        output_filename = f"{job_id}_output.mp4"
        output_path = RENDER_DIR / output_filename
        _composite_frames(
            video_path, begin_frame, end_frame,
            product_path, placed_image, bbox_coords, output_path,
        )

        # Done
        status_callback(job_id, "completed", 100, "", f"/renders/{output_filename}")

    except Exception as e:
        import traceback
        traceback.print_exc()
        status_callback(job_id, "failed", 0, str(e))


def start_processor(job: dict, jobs_store: dict):
    def update(job_id, status, progress, message="", output_url=None):
        if job_id in jobs_store:
            jobs_store[job_id].update({
                "status": status,
                "progress": progress,
                "message": message,
            })
            if output_url:
                jobs_store[job_id]["output_url"] = output_url

    def run():
        try:
            run_job(job, update)
        except Exception as e:
            import traceback
            traceback.print_exc()
            update(job["job_id"], "failed", 0, str(e))

    Thread(target=run, daemon=True).start()
