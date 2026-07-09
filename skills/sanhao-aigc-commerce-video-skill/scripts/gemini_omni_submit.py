#!/usr/bin/env python3
"""Submit a video generation task through Google Gemini Omni Flash API.

Uses Gemini's native video generation via responseModalities=["VIDEO"].
Reads GOOGLE_API_KEY from the environment or a local env-file.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com"
DEFAULT_MODEL = "gemini-2.0-flash-exp"
DEFAULT_ENV_FILE = Path.home() / ".codex" / "secrets" / "google_omni.env"
POLL_INTERVAL = 20
POLL_TIMEOUT = 1800


GENERIC_PRODUCT_LOCK_PREFIX = """\
[Product Appearance Lock] Product appearance is solely defined by the product reference images and the product-specific constraints in this prompt. \
Storyboard frames are only used as reference for shot order, composition, hand/body actions, scenes, lighting, and visual rhythm -- do NOT use them to determine product appearance. \
If the storyboard shows wrong product category, shape, color, material, proportion, missing logo/label/texture/packaging details, treat it as storyboard deviation -- do NOT inherit. \
All shots must maintain the real product's category, structure, color, material, texture, proportion, thickness, edges, and visible key identification details from the product reference images. \
"""

GRID_STORYBOARD_PREFIX = """\
[Nine-Grid Direct Submission Rules] \
Input is a user-provided 3x3 nine-grid storyboard with a confirmed video script. Do NOT run competitor video breakdown. \
The nine-grid storyboard locks 9 shots' reading order (top-to-bottom, left-to-right), composition, subject placement, scenes, lighting, and visual style. \
The video script locks each shot's intent, selling points, pacing, emotional arc, and conversion path. \
Generated video must correspond shot-by-shot -- no skipping, reordering, merging into unrecognizable new shots, or adding scenes/props/actions not in the nine-grid or script. \
All shots must follow real physical world logic: no floating products, no deformed hands, no impossible physics. \
"""


def load_env_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"env file not found: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'\"")
        if key and key not in os.environ:
            os.environ[key] = value


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def request_json(method: str, url: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    headers = {"Content-Type": "application/json"} if payload else {}
    data = None
    if payload is not None:
        data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = resp.read().decode("utf-8")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {exc.code} from Gemini API: {detail}") from exc


def build_lock_prefix(args: argparse.Namespace) -> str:
    blocks: list[str] = []
    if args.reference_mode == "grid-storyboard":
        blocks.append(GRID_STORYBOARD_PREFIX.strip())
    elif args.inject_product_lock:
        blocks.append(GENERIC_PRODUCT_LOCK_PREFIX.strip())
    if args.product_lock:
        blocks.append("[Product-Specific Constraints]\n" + args.product_lock.strip())
    if args.product_lock_file:
        blocks.append("[Product-Specific Constraints]\n" + read_text(args.product_lock_file))
    return "\n\n".join(block for block in blocks if block)


def build_payload(args: argparse.Namespace) -> dict[str, Any]:
    prompt = args.prompt or read_text(args.prompt_file)

    lock_prefix = build_lock_prefix(args)
    if lock_prefix:
        prompt = lock_prefix + "\n\n" + prompt
    if args.reference_note:
        prompt = args.reference_note.strip() + "\n\n" + prompt

    # Build parts: reference images + text prompt
    parts: list[dict[str, Any]] = []
    for path in args.reference_image:
        mime, _ = mimetypes.guess_type(path.name)
        if not mime:
            mime = "image/png"
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        parts.append({
            "inlineData": {
                "mimeType": mime,
                "data": encoded,
            }
        })

    parts.append({"text": prompt})

    # Generation config with video output
    gen_config: dict[str, Any] = {
        "responseModalities": ["TEXT", "VIDEO"],
    }
    if args.temperature is not None:
        gen_config["temperature"] = args.temperature
    if args.seed is not None:
        gen_config["seed"] = args.seed

    payload: dict[str, Any] = {
        "contents": [{"role": "user", "parts": parts}],
        "generationConfig": gen_config,
    }

    return payload


def redacted_payload(payload: dict[str, Any]) -> dict[str, Any]:
    clone = json.loads(json.dumps(payload, ensure_ascii=False))
    for content_item in clone.get("contents", []):
        for part in content_item.get("parts", []):
            if "inlineData" in part:
                mime = part["inlineData"].get("mimeType", "image/png")
                part["inlineData"]["data"] = f"<base64 {mime} omitted>"
    return clone


def download_file(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=300) as resp:
        out_path.write_bytes(resp.read())


def save_base64_video(data: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(data))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Submit a video generation task via Google Gemini Omni Flash."
    )
    parser.add_argument("--prompt-file", type=Path, help="Video prompt text file.")
    parser.add_argument("--prompt", help="Video prompt text.")
    parser.add_argument(
        "--reference-image", type=Path, action="append", default=[],
        help="Reference image path. Pass product images first, then storyboard image.",
    )
    parser.add_argument(
        "--reference-mode", default="replication",
        choices=["replication", "grid-storyboard"],
        help="'replication' expects product images first and storyboard last; 'grid-storyboard' expects a 3x3 grid storyboard.",
    )
    parser.add_argument("--output-dir", type=Path, required=True, help="Directory for task status and downloaded video.")
    parser.add_argument(
        "--env-file", type=Path,
        help=f"Optional env file containing GOOGLE_API_KEY=... Defaults to {DEFAULT_ENV_FILE} when present.",
    )
    parser.add_argument(
        "--base-url", default=os.environ.get("GOOGLE_API_BASE_URL", DEFAULT_BASE_URL),
        help=f"Google API base URL. Defaults to {DEFAULT_BASE_URL}.",
    )
    parser.add_argument("--model", default=os.environ.get("GOOGLE_OMNI_MODEL", DEFAULT_MODEL))
    parser.add_argument("--temperature", type=float, default=None, help="Generation temperature (0.0-2.0).")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--product-lock", help="Optional product appearance lock text.")
    parser.add_argument("--product-lock-file", type=Path, help="Optional file with product appearance constraints.")
    parser.add_argument(
        "--no-product-lock-prefix", dest="inject_product_lock", action="store_false",
        help="Do not prepend the generic product appearance lock block.",
    )
    parser.set_defaults(inject_product_lock=True)
    parser.add_argument(
        "--reference-note",
        help="Optional short note mapping image order.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Write a redacted request preview without submitting.")
    args = parser.parse_args()

    if not args.prompt and not args.prompt_file:
        parser.error("provide --prompt-file or --prompt")
    if not args.reference_image:
        parser.error("provide at least one --reference-image")
    for path in args.reference_image:
        if not path.exists():
            parser.error(f"reference image does not exist: {path}")
    if args.product_lock_file and not args.product_lock_file.exists():
        parser.error(f"product lock file does not exist: {args.product_lock_file}")
    return args


def build_url(base_url: str, model: str, api_key: str) -> str:
    base = base_url.rstrip("/")
    return f"{base}/v1beta/models/{model}:generateContent?key={api_key}"


def main() -> int:
    args = parse_args()

    if args.env_file:
        load_env_file(args.env_file)
    elif not os.environ.get("GOOGLE_API_KEY") and DEFAULT_ENV_FILE.exists():
        load_env_file(DEFAULT_ENV_FILE)

    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GOOGLE_API_KEY is not set. Export it in your shell or pass --env-file.\n"
            f"Recommended env file path: {DEFAULT_ENV_FILE}"
        )

    payload = build_payload(args)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    (args.output_dir / "request.redacted.json").write_text(
        json.dumps(redacted_payload(payload), ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    if args.dry_run:
        print(f"Dry run written: {args.output_dir / 'request.redacted.json'}")
        return 0

    # Submit to Gemini API
    url = build_url(args.base_url, args.model, api_key)
    print(f"Submitting to Gemini {args.model}...")

    result = request_json("POST", url, payload)
    (args.output_dir / "response.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    # Extract video from response
    # Gemini returns video inline as base64 in the response parts
    candidates = result.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates in Gemini response: {result}")

    video_saved = False
    for candidate in candidates:
        parts = candidate.get("content", {}).get("parts", [])
        for i, part in enumerate(parts):
            # Check for inline video data (base64)
            inline = part.get("inlineData", {})
            if inline:
                mime = inline.get("mimeType", "")
                data = inline.get("data", "")
                if "video" in mime:
                    ext = mime.split("/")[-1] if "/" in mime else "mp4"
                    out_video = args.output_dir / f"omni_output_{i}.{ext}"
                    save_base64_video(data, out_video)
                    print(f"Downloaded video: {out_video}  ({mime}, {len(data) * 3 // 4 // 1024} KB)")
                    video_saved = True

            # Check for fileData (uploaded file reference)
            file_data = part.get("fileData", {})
            if file_data:
                file_uri = file_data.get("fileUri", "")
                if file_uri:
                    print(f"Video generated at: {file_uri}")
                    video_saved = True

    if not video_saved:
        # Save full response for debugging
        print(f"No video found in response. Full response saved to {args.output_dir / 'response.json'}")
        # Print text parts if any
        for candidate in candidates:
            for part in candidate.get("content", {}).get("parts", []):
                if "text" in part:
                    print(f"Text response: {part['text'][:500]}")
        raise RuntimeError("Gemini Omni Flash did not return video content. Check response.json for details.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
