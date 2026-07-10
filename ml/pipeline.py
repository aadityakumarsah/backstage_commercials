import os
import sys
import json
import cv2

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ml.select_frame import find_best_product_placement_shot
from ml.insert_product import recursive_placement
from ml.generate_video import generate_video


def run_pipeline(video_path: str, product_path: str, product_description: str) -> str:
    shot = find_best_product_placement_shot(video_path=video_path)

    begin_frame = shot["best_shot_start_frame"]
    end_frame = shot["best_shot_end_frame"]

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Cannot open video: {video_path}")

    cap.set(cv2.CAP_PROP_POS_FRAMES, begin_frame)
    success, frame = cap.read()
    cap.release()

    if not success:
        raise RuntimeError(f"Failed to read frame {begin_frame} from {video_path}")

    background_path = "first_frame.png"
    cv2.imwrite(background_path, frame)
    print(f"Frame {begin_frame} saved as {background_path}")

    final_image, bbox_coords = recursive_placement(
        background_path, product_path, product_description
    )

    output = generate_video(final_image, video_path, begin_frame, end_frame, bbox_coords)
    return output


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run the full product placement pipeline")
    parser.add_argument("video", help="Path to input video file")
    parser.add_argument("product", help="Path to product image (transparent PNG)")
    parser.add_argument("description", help="Product description (e.g. 'Bicycle')")
    args = parser.parse_args()

    output = run_pipeline(args.video, args.product, args.description)
    print(f"\nPipeline complete. Output: {output}")
